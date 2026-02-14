import asyncio
from backend.main import analyze_project
from backend.models import ProjectInput, ConstructionTask
from backend.scheduler import Scheduler
# Mock verify to avoid actually calling LLM in tests if possible, 
# but main.py calls factory. We can use invalid key/provider or mock.
# For this test, we accept the "LLM Validation Failed" message as non-blocking for math verification.

async def run_tests():
    print("--- STARTING FINAL SELF-TESTS ---")

    # Common tasks are defined in main.py, but we need correct IDs to match constraints logic logic if we want perfectly aligned tests?
    # Actually main.py uses DEFAULT_TASKS internally. We can't easily inject tasks into the endpoint function 
    # without mocking. However, the requirement is "Run 3 internal test scenarios". 
    # analyze_project uses DEFAULT_TASKS. So we just vary ProjectInput.

    # Scenario A: Feasible
    # Area=1000, Deadline=200, Budget=5M, Cap=50
    input_a = ProjectInput(
        area=1000, floors=2, deadline=200, budget=10000000, workforce_cap=50, 
        provider="gemini", api_key="test"
    )
    print("\n--- SCENARIO A: FEASIBLE ---")
    try:
        res_a = await analyze_project(input_a)
        print(f"Status: {res_a.feasibility_status}")
        print(f"Duration: {res_a.total_duration} (Deadline: {input_a.deadline})")
        print(f"Cost: {res_a.total_cost.total_cost:,.2f}")
        print(f"Issues: {res_a.constraint_issues}")
    except Exception as e:
        print(f"FAILED: {e}")

    # Scenario B: Deadline Violation + High Risk
    # Tight deadline (e.g. 50 days for same project)
    input_b = ProjectInput(
        area=1000, floors=2, deadline=50, budget=10000000, workforce_cap=50,
        provider="gemini", api_key="test"
    )
    print("\n--- SCENARIO B: DEADLINE VIOLATION ---")
    try:
        res_b = await analyze_project(input_b)
        print(f"Status: {res_b.feasibility_status}")
        print(f"Duration: {res_b.total_duration} (Deadline: {input_b.deadline})")
        print(f"Issues: {res_b.constraint_issues}")
        print(f"Suggestions: {res_b.optimization_suggestions}")
        print(f"Risk Prob: {res_b.simulation_results.deadline_risk_probability}%")
    except Exception as e:
        print(f"FAILED: {e}")

    # Scenario C: Workforce Violation
    # Cap=5 (Very low)
    input_c = ProjectInput(
        area=1000, floors=2, deadline=200, budget=10000000, workforce_cap=5,
        provider="gemini", api_key="test"
    )
    print("\n--- SCENARIO C: WORKFORCE VIOLATION ---")
    try:
        res_c = await analyze_project(input_c)
        print(f"Status: {res_c.feasibility_status}")
        print(f"Workforce Cap: {input_c.workforce_cap}")
        print(f"Issues: {res_c.constraint_issues}")
        print(f"Suggestions: {res_c.optimization_suggestions}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
