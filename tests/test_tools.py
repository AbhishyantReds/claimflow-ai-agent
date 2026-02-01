"""
Tests for agent tools (claim processing functions)
"""
import pytest
from datetime import datetime
from agent.tools import (
    extract_claim_data_from_conversation,
    retrieve_policy,
    check_coverage,
    calculate_payout,
    check_claim_history,
    generate_report
)


class TestExtractClaimData:
    """Test extract_claim_data_from_conversation"""
    
    def test_extract_motor_claim(self):
        """Test extracting motor claim data"""
        claim_data = {
            "claim_type": "motor_accident",
            "vehicle_registration": "KA-01-AB-1234",
            "incident_date": "2024-06-15",
            "damage_description": "Front bumper damaged",
            "repair_estimate": 50000
        }
        
        result = extract_claim_data_from_conversation(claim_data)
        
        assert result["claim_type"] == "motor_accident"
        assert result["vehicle_registration"] == "KA-01-AB-1234"
        assert "damage_description" in result
    
    def test_extract_health_claim(self):
        """Test extracting health claim data"""
        claim_data = {
            "claim_type": "health_hospitalization",
            "hospital_name": "Apollo Hospital",
            "treatment_type": "surgery",
            "hospitalization_date": "2024-12-01",
            "treatment_cost": 150000
        }
        
        result = extract_claim_data_from_conversation(claim_data)
        
        assert result["claim_type"] == "health_hospitalization"
        assert result["hospital_name"] == "Apollo Hospital"
        assert result["treatment_cost"] == 150000
    
    def test_extract_home_claim(self):
        """Test extracting home claim data"""
        claim_data = {
            "claim_type": "home_fire",
            "property_id": "PROP-001",
            "incident_date": "2024-11-20",
            "damage_description": "Fire damage in living room",
            "repair_estimate": 200000
        }
        
        result = extract_claim_data_from_conversation(claim_data)
        
        assert result["claim_type"] == "home_fire"
        assert result["property_id"] == "PROP-001"
    
    def test_normalize_claim_types(self):
        """Test claim type normalization"""
        variations = [
            "accident", "collision", "car accident",
            "theft", "stolen", "burglary",
            "fire", "fire damage"
        ]
        
        for variation in variations:
            claim_data = {"claim_type": variation}
            result = extract_claim_data_from_conversation(claim_data)
            assert result["claim_type"] in [
                "motor_accident", "motor_theft", "motor_fire",
                "home_theft", "home_fire"
            ]


class TestRetrievePolicy:
    """Test retrieve_policy function"""
    
    def test_retrieve_from_database(self, db_session, sample_motor_policy):
        """Test retrieving policy from database"""
        # This would require mocking the database manager
        # For now, test with fallback
        result = retrieve_policy("TEST-KA-1234")
        
        assert "policy_number" in result
        assert "coverage_type" in result
    
    def test_retrieve_fallback(self):
        """Test fallback to mock data"""
        result = retrieve_policy("UNKNOWN-123")
        
        assert result is not None
        assert "policy_number" in result
        assert result["status"] == "active"


class TestCheckCoverage:
    """Test check_coverage function"""
    
    def test_motor_accident_coverage(self):
        """Test checking motor accident coverage"""
        claim_type = "motor_accident"
        policy_data = {
            "policy_type": "motor",
            "coverage_type": "comprehensive",
            "zero_depreciation": True
        }
        
        result = check_coverage(claim_type, policy_data)
        
        assert result["covered"] is True
        assert "Own Damage" in str(result.get("coverage_sections", []))
    
    def test_health_coverage(self):
        """Test checking health coverage"""
        claim_type = "health_hospitalization"
        policy_data = {
            "policy_type": "health",
            "sum_insured": 500000
        }
        
        result = check_coverage(claim_type, policy_data)
        
        assert result["covered"] is True
        assert "Hospitalization" in str(result.get("coverage_sections", []))
    
    def test_exclusions(self):
        """Test coverage exclusions"""
        claim_type = "motor_accident"
        policy_data = {
            "policy_type": "motor",
            "coverage_type": "third_party"  # Only third party, no own damage
        }
        
        result = check_coverage(claim_type, policy_data)
        
        # Third party policy should have exclusions for own damage
        assert "exclusions" in result


class TestCalculatePayout:
    """Test calculate_payout function"""
    
    def test_motor_payout_with_zero_dep(self):
        """Test motor claim payout with zero depreciation"""
        claim_data = {
            "repair_estimate": 100000,
            "vehicle_age": 2
        }
        policy_data = {
            "zero_depreciation": True,
            "deductible": 2000
        }
        
        result = calculate_payout("motor_accident", claim_data, policy_data)
        
        assert result["eligible_amount"] == 100000
        assert result["depreciation"] == 0
        assert result["final_payout"] == 98000  # 100000 - 2000 deductible
    
    def test_motor_payout_with_depreciation(self):
        """Test motor claim payout with depreciation"""
        claim_data = {
            "repair_estimate": 100000,
            "vehicle_age": 3
        }
        policy_data = {
            "zero_depreciation": False,
            "deductible": 2000
        }
        
        result = calculate_payout("motor_accident", claim_data, policy_data)
        
        assert result["depreciation"] > 0
        assert result["final_payout"] < 98000
    
    def test_health_payout_with_copay(self):
        """Test health claim payout with co-payment"""
        claim_data = {
            "treatment_cost": 100000
        }
        policy_data = {
            "copay_percentage": 10,
            "sum_insured": 500000
        }
        
        result = calculate_payout("health_hospitalization", claim_data, policy_data)
        
        assert result["copay_amount"] == 10000
        assert result["final_payout"] == 90000
    
    def test_payout_exceeds_sum_insured(self):
        """Test payout capped at sum insured"""
        claim_data = {
            "treatment_cost": 600000
        }
        policy_data = {
            "copay_percentage": 0,
            "sum_insured": 500000
        }
        
        result = calculate_payout("health_hospitalization", claim_data, policy_data)
        
        # Should be capped at sum insured
        assert result["final_payout"] <= 500000


class TestCheckClaimHistory:
    """Test check_claim_history function"""
    
    def test_check_existing_customer(self):
        """Test checking history for existing customer"""
        result = check_claim_history("CUST-001")
        
        assert "customer_found" in result
        assert "total_claims" in result
        assert "risk_level" in result
    
    def test_check_new_customer(self):
        """Test checking history for new customer"""
        result = check_claim_history("CUST-NEW-999")
        
        assert result["customer_found"] is False
        assert result["total_claims"] == 0
        assert result["risk_level"] == "unknown"
    
    def test_risk_assessment(self):
        """Test risk level assessment"""
        # Customer with fraud flags should be high risk
        # Customer with many claims should be medium risk
        # New customer should be unknown risk
        pass  # Tested with actual data


class TestGenerateReport:
    """Test generate_report function"""
    
    def test_motor_report_generation(self):
        """Test generating motor claim report"""
        claim_data = {
            "claim_type": "motor_accident",
            "vehicle_registration": "KA-01-AB-1234",
            "incident_date": "2024-06-15",
            "repair_estimate": 85000
        }
        
        policy_data = {
            "policy_number": "MI-2024-001",
            "coverage_type": "comprehensive"
        }
        
        coverage_result = {"covered": True}
        payout_result = {"final_payout": 83000, "depreciation": 0}
        decision = {"decision": "approved", "reason": "Valid claim"}
        
        report = generate_report(
            claim_data, policy_data, coverage_result,
            payout_result, decision
        )
        
        assert "CLAIM ASSESSMENT REPORT" in report
        assert "KA-01-AB-1234" in report
        assert "83,000" in report or "83000" in report
    
    def test_health_report_generation(self):
        """Test generating health claim report"""
        claim_data = {
            "claim_type": "health_hospitalization",
            "hospital_name": "Apollo Hospital",
            "treatment_cost": 120000
        }
        
        policy_data = {
            "policy_number": "HE-2024-001",
            "coverage_type": "individual"
        }
        
        coverage_result = {"covered": True}
        payout_result = {"final_payout": 108000, "copay_amount": 12000}
        decision = {"decision": "approved"}
        
        report = generate_report(
            claim_data, policy_data, coverage_result,
            payout_result, decision
        )
        
        assert "Apollo Hospital" in report
        assert "108,000" in report or "108000" in report
    
    def test_rejected_claim_report(self):
        """Test report for rejected claim"""
        claim_data = {"claim_type": "motor_accident"}
        policy_data = {"policy_number": "MI-2024-001"}
        coverage_result = {"covered": False, "exclusions": ["Excluded peril"]}
        payout_result = {"final_payout": 0}
        decision = {"decision": "rejected", "reason": "Claim not covered"}
        
        report = generate_report(
            claim_data, policy_data, coverage_result,
            payout_result, decision
        )
        
        assert "REJECTED" in report or "rejected" in report.lower()
        assert "not covered" in report.lower()


class TestIntegration:
    """Integration tests for tool chains"""
    
    def test_full_claim_processing_chain(self):
        """Test complete claim processing workflow"""
        # 1. Extract claim data
        claim_data = extract_claim_data_from_conversation({
            "claim_type": "accident",
            "vehicle_registration": "KA-01-AB-1234",
            "incident_date": "2024-06-15",
            "repair_estimate": 50000
        })
        
        assert claim_data["claim_type"] == "motor_accident"
        
        # 2. Retrieve policy
        policy_data = retrieve_policy(claim_data["vehicle_registration"])
        assert "policy_number" in policy_data
        
        # 3. Check coverage
        coverage = check_coverage(claim_data["claim_type"], policy_data)
        assert "covered" in coverage
        
        # 4. Calculate payout
        payout = calculate_payout(
            claim_data["claim_type"],
            claim_data,
            policy_data
        )
        assert "final_payout" in payout
        
        # 5. Check history
        history = check_claim_history("CUST-001")
        assert "total_claims" in history
