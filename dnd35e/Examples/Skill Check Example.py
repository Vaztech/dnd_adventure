from dnd35e import SkillCheck

# Make a Hide check
skill_rank = 5  # 5 ranks in Hide
dex_mod = 3     # Dex modifier
dc = 15         # Difficulty Class
modifiers = {"Cover": 4}  # +4 for good cover

result = SkillCheck.make_check(skill_rank, dex_mod, dc, modifiers)

print(f"Hide check: d20 ({result['roll']}) + skill ({skill_rank}) + Dex ({dex_mod}) + modifiers ({sum(modifiers.values())}) = {result['total']} vs DC {dc}")
print(f"Result: {'Success!' if result['success'] else 'Failure'}")
print(f"Degree of success: {result['degree_of_success']}")