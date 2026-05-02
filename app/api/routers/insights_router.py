"""
Insights router — powers the /insights ML Intelligence page.
All heavy computation is done server-side; the frontend only renders.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import Counter
import json
from datetime import date

from database.session import get_db
from app.models.opportunity import Opportunity
from app.models.recommendation import Recommendation
from app.models.user import User
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/insights", tags=["insights"])


def _skills(raw) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC  –  no auth required
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/public")
async def get_public_insights(db: AsyncSession = Depends(get_db)):
    """
    Public stats used on the non-authenticated parts of /insights:
    skill frequency, cluster composition, deadline buckets, type/category breakdown.
    """
    result = await db.execute(select(Opportunity))
    opps = result.scalars().all()

    skill_counter: Counter = Counter()
    cluster_skills: dict[int, Counter] = {}
    cluster_labels: dict[int, str] = {}

    for opp in opps:
        skills = _skills(opp.skills_required)
        for s in skills:
            skill_counter[s.lower()] += 1
        if opp.cluster_id is not None:
            cid = opp.cluster_id
            if cid not in cluster_skills:
                cluster_skills[cid] = Counter()
                cluster_labels[cid] = opp.cluster_label or f"Cluster {cid}"
            for s in skills:
                cluster_skills[cid][s.lower()] += 1

    # cluster composition
    cluster_comp: dict[int, dict] = {}
    for opp in opps:
        cid = opp.cluster_id
        if cid is None:
            continue
        if cid not in cluster_comp:
            cluster_comp[cid] = {
                "cluster_id": cid,
                "label": cluster_labels.get(cid, f"Cluster {cid}"),
                "total": 0,
                "by_type": {},
                "by_category": {},
                "top_skills": [s for s, _ in (cluster_skills.get(cid) or Counter()).most_common(8)],
            }
        cluster_comp[cid]["total"] += 1
        t = opp.type
        cat = opp.category
        cluster_comp[cid]["by_type"][t] = cluster_comp[cid]["by_type"].get(t, 0) + 1
        cluster_comp[cid]["by_category"][cat] = cluster_comp[cid]["by_category"].get(cat, 0) + 1

    # deadline buckets
    today = date.today()
    dl_buckets = {"expired": 0, "0-7d": 0, "8-30d": 0, "31-90d": 0, "90+d": 0}
    for opp in opps:
        if not opp.deadline:
            continue
        try:
            days = (date.fromisoformat(str(opp.deadline)) - today).days
            if days < 0:       dl_buckets["expired"] += 1
            elif days <= 7:    dl_buckets["0-7d"] += 1
            elif days <= 30:   dl_buckets["8-30d"] += 1
            elif days <= 90:   dl_buckets["31-90d"] += 1
            else:              dl_buckets["90+d"] += 1
        except Exception:
            pass

    return {
        "total_opportunities": len(opps),
        "total_unique_skills": len(skill_counter),
        "skill_frequency": [{"skill": s, "count": c} for s, c in skill_counter.most_common(30)],
        "clusters": sorted(cluster_comp.values(), key=lambda x: x["cluster_id"]),
        "deadline_distribution": dl_buckets,
        "type_distribution": dict(Counter(o.type for o in opps)),
        "category_distribution": dict(Counter(o.category for o in opps)),
    }


# ─────────────────────────────────────────────────────────────────────────────
# PERSONAL  –  auth required
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/personal")
async def get_personal_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Personalized ML intelligence for the logged-in user.
    Returns all data needed for sections 1-5 of the /insights page.
    """
    user_skills_raw = _skills(current_user.skills)
    user_skills = set(s.lower() for s in user_skills_raw)
    user_level = (current_user.level or "master").lower()

    # ── load everything ───────────────────────────────────────────────────────
    opp_result = await db.execute(select(Opportunity))
    opps = opp_result.scalars().all()

    rec_result = await db.execute(
        select(Recommendation)
        .where(Recommendation.user_id == current_user.user_id)
        .order_by(Recommendation.score.desc())
    )
    user_recs = rec_result.scalars().all()

    # ── build cluster maps ────────────────────────────────────────────────────
    cluster_skills: dict[int, Counter] = {}
    cluster_labels: dict[int, str] = {}
    opp_by_id: dict[str, Opportunity] = {o.id: o for o in opps}

    for opp in opps:
        cid = opp.cluster_id
        if cid is None:
            continue
        if cid not in cluster_skills:
            cluster_skills[cid] = Counter()
            cluster_labels[cid] = opp.cluster_label or f"Cluster {cid}"
        for s in _skills(opp.skills_required):
            cluster_skills[cid][s.lower()] += 1

    # ── find user's top cluster (by rec count) ────────────────────────────────
    rec_cluster_counts: Counter = Counter()
    for rec in user_recs:
        opp = opp_by_id.get(rec.opportunity_id)
        if opp and opp.cluster_id is not None:
            rec_cluster_counts[opp.cluster_id] += 1

    top_cid = rec_cluster_counts.most_common(1)[0][0] if rec_cluster_counts else 0

    # ── SECTION 1 — Skill Genome ──────────────────────────────────────────────
    all_required: Counter = Counter()
    for opp in opps:
        for s in _skills(opp.skills_required):
            all_required[s.lower()] += 1

    top_cluster_top = set(s for s, _ in (cluster_skills.get(top_cid) or Counter()).most_common(12))

    skill_genome = []
    for skill, freq in all_required.most_common(45):
        in_top = skill in top_cluster_top
        has = skill in user_skills
        status = "matched" if has else ("gap" if in_top else "irrelevant")
        skill_genome.append({"skill": skill, "frequency": freq, "status": status, "in_top_cluster": in_top})

    top_cluster_list = [(s, c) for s, c in (cluster_skills.get(top_cid) or Counter()).most_common(12)]
    matched_in_top = sum(1 for s, _ in top_cluster_list if s in user_skills)
    coverage_pct = round(matched_in_top / len(top_cluster_list) * 100) if top_cluster_list else 0

    # ── SECTION 2 — Skill Gap Radar ───────────────────────────────────────────
    radar_data = []
    for cid in sorted(cluster_skills.keys()):
        top8 = [(s, c) for s, c in cluster_skills[cid].most_common(8)]
        user_pct = round(sum(1 for s, _ in top8 if s in user_skills) / len(top8) * 100) if top8 else 0
        radar_data.append({
            "cluster": cluster_labels.get(cid, f"C{cid}"),
            "cluster_id": cid,
            "user_coverage": user_pct,
            "ideal": 100,
        })

    # skills that unlock the most currently-unmatched opportunities
    unlocks: Counter = Counter()
    for opp in opps:
        opp_skills = set(s.lower() for s in _skills(opp.skills_required))
        if not (user_skills & opp_skills):           # zero overlap
            for s in (opp_skills - user_skills):
                unlocks[s] += 1

    skill_gaps = [
        {"skill": s, "unlocks": c, "frequency": int(all_required.get(s, 0))}
        for s, c in unlocks.most_common(6)
    ]

    # ── SECTION 3 — Score Anatomy ─────────────────────────────────────────────
    today = date.today()
    level_order = ["bachelor", "master", "phd", "postdoc", "professional"]
    score_anatomy = []

    for rec in user_recs[:3]:
        opp = opp_by_id.get(rec.opportunity_id)
        if not opp:
            continue

        opp_skills = set(s.lower() for s in _skills(opp.skills_required))
        skill_overlap = list(user_skills & opp_skills)

        # recency
        deadline_days = None
        recency = 0.3
        if opp.deadline:
            try:
                deadline_days = (date.fromisoformat(str(opp.deadline)) - today).days
                if deadline_days < 0:        recency = 0.0
                elif deadline_days <= 7:     recency = 0.2
                elif deadline_days <= 14:    recency = 0.4
                elif deadline_days <= 30:    recency = 0.6
                elif deadline_days <= 60:    recency = 0.8
                else:                        recency = 1.0
            except Exception:
                pass

        # level
        elig = (opp.eligibility or "").lower()
        if not elig:
            level_score = 0.5
        elif user_level in elig or "all" in elig or "any" in elig:
            level_score = 1.0
        else:
            level_score = 0.5

        similarity = max(0.0, round((rec.score - 0.3 * level_score - 0.2 * recency) / 0.5, 3))

        score_anatomy.append({
            "opportunity_id": opp.id,
            "title": opp.title,
            "type": opp.type,
            "category": opp.category,
            "total_score": round(rec.score, 4),
            "components": {
                "semantic_similarity": similarity,
                "level_alignment": round(level_score, 3),
                "deadline_recency": round(recency, 3),
            },
            "skill_overlap": skill_overlap[:5],
            "deadline_days": deadline_days,
            "eligibility": opp.eligibility,
            "match_reasons": _skills(rec.match_reasons),
        })

    # ── SECTION 4 — Landscape (scatter) ──────────────────────────────────────
    landscape = []
    for rec in user_recs:
        opp = opp_by_id.get(rec.opportunity_id)
        if not opp:
            continue
        deadline_days = 365
        if opp.deadline:
            try:
                deadline_days = max(0, (date.fromisoformat(str(opp.deadline)) - today).days)
            except Exception:
                pass
        opp_skills = set(s.lower() for s in _skills(opp.skills_required))
        landscape.append({
            "id": opp.id,
            "title": opp.title,
            "type": opp.type,
            "category": opp.category,
            "score": round(rec.score, 4),
            "deadline_days": deadline_days,
            "skill_match_count": len(user_skills & opp_skills),
            "url": opp.url,
        })

    return {
        "user": {
            "name": current_user.name,
            "level": user_level,
            "skills": user_skills_raw,
            "skill_count": len(user_skills_raw),
        },
        "top_cluster": {
            "cluster_id": top_cid,
            "label": cluster_labels.get(top_cid, "Unknown"),
            "coverage_pct": coverage_pct,
            "matched": matched_in_top,
            "total": len(top_cluster_list),
        },
        "skill_genome": skill_genome,
        "radar_data": radar_data,
        "skill_gaps": skill_gaps,
        "score_anatomy": score_anatomy,
        "landscape": landscape,
    }
