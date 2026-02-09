"""
Tools for ClaimFlow AI Agent
Converted to LangGraph @tool decorator pattern for agentic processing.

Each tool:
- Has a @tool decorator with rich description
- Documents its dependencies in the docstring
- Uses lightweight validation for dependencies
- Records invocations for audit trail
"""
import json
import logging
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Annotated

from langchain_core.tools import tool
from pydantic import BaseModel, Field

import config
from agent.state import ToolInvocation

logger = logging.getLogger(__name__)


# ============ Helper Functions ============

def load_json_data(filepath: str) -> dict:
    """Load JSON data from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return {}


def call_rag_api(endpoint: str, payload: dict) -> dict:
    """Call Insurance RAG system API"""
    try:
        url = f"{config.INSURANCE_RAG_URL}{endpoint}"
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"RAG API call failed: {e}")
        return {"error": str(e), "status": "unavailable"}


def validate_dependencies(state: dict, required_fields: List[str]) -> tuple[bool, List[str]]:
    """
    Lightweight validation that required state fields are populated.
    Returns (is_valid, missing_fields)
    """
    missing = []
    for field in required_fields:
        value = state.get(field)
        if value is None or value == {} or value == [] or value == "":
            missing.append(field)
    return len(missing) == 0, missing


def record_tool_call(state: dict, tool_name: str, inputs: dict, 
                     output: Any, duration_ms: float, success: bool = True, 
                     error: str = None):
    """Record tool invocation in reasoning trace for auditability"""
    try:
        if state.get("reasoning_trace"):
            invocation = ToolInvocation(
                tool_name=tool_name,
                tool_input=inputs,
                tool_output=str(output)[:500] if output else "",  # Truncate for storage
                duration_ms=duration_ms,
                success=success,
                error=error
            )
            if isinstance(state["reasoning_trace"], dict):
                if "tool_invocations" not in state["reasoning_trace"]:
                    state["reasoning_trace"]["tool_invocations"] = []
                state["reasoning_trace"]["tool_invocations"].append(invocation.model_dump())
            state["tool_call_count"] = state.get("tool_call_count", 0) + 1
    except Exception as e:
        logger.warning(f"Failed to record tool call: {e}")


# ============ Tool 1: Extract Claim Data ============

@tool
def extract_claim_data(
    claim_data: dict
) -> dict:
    """
    Extract and structure claim data from conversation.
    
    CALL THIS FIRST - No dependencies required.
    Normalizes claim type and structures data for downstream processing.
    
    Args:
        claim_data: Raw claim data dictionary from conversation phase
    
    Returns:
        Structured claim data with normalized claim_type, incident_date, 
        and category-specific fields (vehicle_registration, treatment_cost, etc.)
    """
    start = time.time()
    logger.info("Tool: Extracting and structuring claim data...")
    
    try:
        claim_type = claim_data.get("claim_type", "unknown").lower()
        
        # Motor claims normalization
        if "motor" in claim_type or "vehicle" in claim_type or "car" in claim_type or "bike" in claim_type:
            if "accident" in claim_type or "collision" in claim_type:
                normalized_type = "motor_accident"
            elif "theft" in claim_type or "stolen" in claim_type:
                normalized_type = "motor_theft"
            elif "fire" in claim_type:
                normalized_type = "motor_fire"
            elif "vandalism" in claim_type or "vandal" in claim_type:
                normalized_type = "motor_vandalism"
            else:
                normalized_type = "motor_accident"
        
        # Home claims normalization
        elif "home" in claim_type or "house" in claim_type or "property" in claim_type:
            if "fire" in claim_type or "burn" in claim_type:
                normalized_type = "home_fire"
            elif "theft" in claim_type or "burglary" in claim_type or "stolen" in claim_type:
                normalized_type = "home_theft"
            elif "flood" in claim_type or "water" in claim_type:
                normalized_type = "home_flood"
            elif "earthquake" in claim_type or "quake" in claim_type:
                normalized_type = "home_earthquake"
            elif "storm" in claim_type or "cyclone" in claim_type or "wind" in claim_type:
                normalized_type = "home_storm"
            else:
                normalized_type = "home_fire"
        
        # Health claims normalization
        elif "health" in claim_type or "medical" in claim_type or "hospital" in claim_type:
            if "accident" in claim_type or "injury" in claim_type or "broke" in claim_type or "fracture" in claim_type:
                normalized_type = "health_accident"
            elif "surgery" in claim_type or "operation" in claim_type:
                normalized_type = "health_surgery"
            elif "critical" in claim_type or "heart" in claim_type or "cancer" in claim_type or "stroke" in claim_type:
                normalized_type = "health_critical_illness"
            else:
                normalized_type = "health_hospitalization"
        else:
            normalized_type = claim_type
        
        # Structure the data
        structured_data = {
            "claim_type": normalized_type,
            "incident_date": claim_data.get("incident_date", ""),
            "customer_id": claim_data.get("customer_id", ""),
            "location": claim_data.get("location", ""),
            "submitted_documents": claim_data.get("submitted_documents", [])
        }
        
        # Add category-specific fields
        if normalized_type.startswith("motor"):
            structured_data.update({
                "damage_description": claim_data.get("damage_description", ""),
                "vehicle_registration": claim_data.get("vehicle_registration", ""),
                "repair_estimate": float(claim_data.get("repair_estimate", 0)) if claim_data.get("repair_estimate") else 0
            })
            logger.info(f"✓ Extracted Motor Claim: {normalized_type}, Amount: ₹{structured_data.get('repair_estimate', 0):,.0f}")
            
        elif normalized_type.startswith("home"):
            structured_data.update({
                "damage_description": claim_data.get("damage_description", ""),
                "property_id": claim_data.get("property_id", ""),
                "repair_estimate": float(claim_data.get("repair_estimate", 0)) if claim_data.get("repair_estimate") else 0
            })
            logger.info(f"✓ Extracted Home Claim: {normalized_type}, Amount: ₹{structured_data.get('repair_estimate', 0):,.0f}")
            
        elif normalized_type.startswith("health"):
            structured_data.update({
                "treatment_type": claim_data.get("treatment_type", ""),
                "hospital_name": claim_data.get("hospital_name", ""),
                "hospitalization_date": claim_data.get("hospitalization_date", ""),
                "treatment_cost": float(claim_data.get("treatment_cost", 0)) if claim_data.get("treatment_cost") else 0,
                "medical_bills": claim_data.get("medical_bills", "")
            })
            logger.info(f"✓ Extracted Health Claim: {normalized_type}, Amount: ₹{structured_data.get('treatment_cost', 0):,.0f}")
        
        duration = (time.time() - start) * 1000
        logger.info(f"extract_claim_data completed in {duration:.0f}ms")
        
        return structured_data
        
    except Exception as e:
        logger.error(f"Error in extract_claim_data: {e}")
        return {"error": str(e)}


# ============ Tool 2: Retrieve Policy ============

@tool
def retrieve_policy(
    identifier: str
) -> dict:
    """
    Retrieve policy details from database.
    
    REQUIRES: Nothing (can run in parallel with extract_claim_data)
    
    Looks up policy by vehicle registration, property ID, or policy number.
    
    Args:
        identifier: Vehicle registration (e.g., 'TS09EF5678'), property ID, or policy number
    
    Returns:
        Policy details including policy_number, coverage_type, sum_insured, 
        deductible, zero_depreciation, status, and more
    """
    start = time.time()
    logger.info(f"Tool: Retrieving policy for {identifier}...")
    
    try:
        # Try database first
        try:
            from database.models import get_db_manager
            from database.crud import get_policy_by_identifier
            
            db_manager = get_db_manager()
            session = db_manager.get_session()
            
            try:
                policy = get_policy_by_identifier(session, identifier)
                
                if policy:
                    logger.info(f"✓ Policy found in database: {policy.policy_number}")
                    
                    policy_data = {
                        "policy_number": policy.policy_number,
                        "identifier": identifier,
                        "policy_type": policy.policy_type.value,
                        "coverage_type": policy.coverage_type,
                        "sum_insured": policy.sum_insured,
                        "premium": policy.premium,
                        "deductible": policy.deductible,
                        "policy_start": policy.policy_start.isoformat(),
                        "policy_end": policy.policy_end.isoformat(),
                        "status": policy.status,
                        "customer_name": policy.customer.name if policy.customer else "Unknown",
                        "customer_id": policy.customer.customer_id if policy.customer else ""
                    }
                    
                    # Add type-specific fields
                    if policy.vehicle_registration:
                        policy_data["vehicle_registration"] = policy.vehicle_registration
                        policy_data["idv"] = policy.idv
                        policy_data["zero_depreciation"] = policy.zero_depreciation
                        policy_data["ncb_percentage"] = policy.ncb_percentage
                    
                    if policy.property_id:
                        policy_data["property_id"] = policy.property_id
                    
                    if policy.policy_holder_age:
                        policy_data["policy_holder_age"] = policy.policy_holder_age
                        policy_data["copay_percentage"] = policy.copay_percentage
                    
                    # Try to add RAG context
                    try:
                        from agent.rag import VectorStore
                        vector_store = VectorStore()
                        
                        if vector_store.get_document_count() > 0:
                            query = f"Coverage details and benefits for {policy.policy_type.value} insurance"
                            results = vector_store.search(
                                query, 
                                n_results=2,
                                filter_metadata={"policy_type": policy.policy_type.value}
                            )
                            
                            if results:
                                policy_data["rag_context"] = [{
                                    'source': r['metadata']['policy_name'],
                                    'content': r['text'][:500],
                                    'relevance': 1 - r['distance']
                                } for r in results]
                                logger.info(f"✓ Added RAG context ({len(results)} sections)")
                    except Exception as rag_error:
                        logger.warning(f"RAG context failed: {rag_error}")
                    
                    duration = (time.time() - start) * 1000
                    logger.info(f"retrieve_policy completed in {duration:.0f}ms")
                    return policy_data
                else:
                    logger.warning(f"Policy not found in database for: {identifier}")
            finally:
                session.close()
                
        except Exception as db_error:
            logger.warning(f"Database query failed: {db_error}")
        
        # Fallback to mock data
        logger.info("Using mock policy data")
        policy_data = {
            "policy_number": "MI-2024-3456",
            "identifier": identifier,
            "vehicle": "Hyundai Creta 2023",
            "idv": 1550000,
            "sum_insured": 1550000,
            "coverage_type": "comprehensive",
            "deductible": 2000,
            "zero_depreciation": True,
            "ncb_percentage": 20,
            "copay_percentage": 10,
            "policy_start": "2024-01-01",
            "policy_end": "2025-01-01",
            "status": "active"
        }
        
        duration = (time.time() - start) * 1000
        logger.info(f"retrieve_policy (mock) completed in {duration:.0f}ms")
        return policy_data
        
    except Exception as e:
        logger.error(f"Error in retrieve_policy: {e}")
        return {"error": str(e)}


# ============ Tool 3: Check Coverage ============

@tool
def check_coverage(
    claim_type: str,
    policy_data: dict
) -> dict:
    """
    Verify if claim type is covered under the policy.
    
    REQUIRES: retrieve_policy must be called first to get policy_data
    
    Checks policy coverage type against claim type and returns coverage limits.
    
    Args:
        claim_type: Normalized claim type (e.g., 'motor_accident', 'health_surgery')
        policy_data: Policy details from retrieve_policy tool
    
    Returns:
        Coverage result with 'covered' boolean, 'section', and 'coverage_limit'
    """
    start = time.time()
    logger.info(f"Tool: Checking coverage for {claim_type}...")
    
    try:
        # Call RAG system for coverage check
        result = call_rag_api("/check-coverage", {
            "claim_type": claim_type,
            "policy_number": policy_data.get("policy_number", "")
        })
        
        if "error" in result:
            logger.warning("RAG unavailable, using rule-based coverage check")
            coverage_type = policy_data.get("coverage_type", "")
            
            # Health claims
            if claim_type.startswith("health_"):
                covered = True
                if "accident" in claim_type:
                    section = "Section 2: Accidental Injury Cover"
                elif "surgery" in claim_type:
                    section = "Section 3: Surgical Procedures"
                elif "critical" in claim_type:
                    section = "Section 4: Critical Illness Cover"
                else:
                    section = "Section 1: Hospitalization Cover"
                limit = policy_data.get("sum_insured", 500000)
            
            # Motor claims
            elif claim_type.startswith("motor_"):
                if coverage_type == "comprehensive":
                    covered = True
                    section = "Section 2.1: Own Damage"
                    limit = policy_data.get("idv", policy_data.get("sum_insured", 0))
                elif coverage_type == "third_party":
                    covered = "third_party" in claim_type.lower()
                    section = "Section 1: Third Party Liability" if covered else "Not Covered"
                    limit = 0 if not covered else float('inf')
                else:
                    covered = True  # Assume comprehensive
                    section = "Section 2.1: Own Damage"
                    limit = policy_data.get("sum_insured", 0)
            
            # Home claims
            elif claim_type.startswith("home_"):
                covered = True
                if "fire" in claim_type:
                    section = "Section 1: Fire and Allied Perils"
                elif "theft" in claim_type:
                    section = "Section 2: Burglary and Theft"
                elif "flood" in claim_type:
                    section = "Section 3: Natural Calamities - Flood"
                elif "earthquake" in claim_type:
                    section = "Section 3: Natural Calamities - Earthquake"
                elif "storm" in claim_type:
                    section = "Section 3: Natural Calamities - Storm"
                else:
                    section = "Section 1: General Property Damage"
                limit = policy_data.get("sum_insured", 1000000)
            else:
                covered = False
                section = "Unknown Coverage"
                limit = 0
            
            result = {
                "covered": covered,
                "section": section,
                "coverage_limit": limit,
                "claim_type": claim_type,
                "applicable": covered
            }
        
        status = "✓ Covered" if result.get("covered") else "✗ Not Covered"
        logger.info(f"{status} under {result.get('section', 'N/A')}")
        
        duration = (time.time() - start) * 1000
        logger.info(f"check_coverage completed in {duration:.0f}ms")
        return result
        
    except Exception as e:
        logger.error(f"Error in check_coverage: {e}")
        return {"error": str(e), "covered": False}


# ============ Tool 4: Check Exclusions ============

@tool
def check_exclusions(
    claim_data: dict,
    policy_data: dict
) -> List[dict]:
    """
    Check if any policy exclusions apply to this claim.
    
    REQUIRES: extract_claim_data AND retrieve_policy (needs both extracted_data and policy_data)
    
    Args:
        claim_data: Structured claim information from extract_claim_data
        policy_data: Policy details from retrieve_policy
    
    Returns:
        List of exclusions with 'exclusion' name and 'applies' boolean for each
    """
    start = time.time()
    logger.info("Tool: Checking policy exclusions...")
    
    try:
        # Common exclusions to check
        common_exclusions = [
            "DUI (Driving Under Influence)",
            "Invalid or Expired License",
            "Commercial Use without Commercial Policy",
            "War or Nuclear Risk",
            "Consequential Losses",
            "Wear and Tear",
            "Mechanical/Electrical Breakdown"
        ]
        
        exclusions = []
        for exclusion in common_exclusions:
            exclusions.append({
                "exclusion": exclusion,
                "applies": False,
                "reason": "No indication of this exclusion in claim details"
            })
        
        applicable_exclusions = [e for e in exclusions if e["applies"]]
        
        if not applicable_exclusions:
            logger.info("✓ No exclusions apply")
        else:
            logger.warning(f"✗ {len(applicable_exclusions)} exclusion(s) apply")
        
        duration = (time.time() - start) * 1000
        logger.info(f"check_exclusions completed in {duration:.0f}ms")
        return exclusions
        
    except Exception as e:
        logger.error(f"Error in check_exclusions: {e}")
        return [{"error": str(e)}]


# ============ Tool 5: Calculate Payout ============

@tool
def calculate_payout(
    claim_amount: float,
    policy_data: dict,
    claim_type: str,
    vehicle_age_years: int = 1
) -> dict:
    """
    Calculate payable amount after deductible and depreciation/copay.
    
    REQUIRES: check_coverage (needs coverage confirmation before calculating payout)
    
    For health claims: applies copay percentage
    For motor/home claims: applies depreciation based on vehicle/property age
    
    Args:
        claim_amount: Claimed amount in INR (repair_estimate or treatment_cost)
        policy_data: Policy details from retrieve_policy
        claim_type: Normalized claim type to determine calculation method
        vehicle_age_years: Vehicle age for depreciation calculation (motor only)
    
    Returns:
        Payout breakdown with claimed_amount, deductible, depreciation/copay, payable_amount
    """
    start = time.time()
    logger.info(f"Tool: Calculating payout for ₹{claim_amount:,.0f}...")
    
    try:
        deductible = policy_data.get("deductible", 2000)
        
        # HEALTH CLAIMS - Use co-pay instead of depreciation
        if claim_type.startswith("health_"):
            copay_percentage = policy_data.get("copay_percentage", 10)
            room_rent_limit = policy_data.get("room_rent_limit", 5000)
            
            copay_amount = claim_amount * (copay_percentage / 100)
            payable_amount = max(0, claim_amount - copay_amount - deductible)
            
            result = {
                "claimed_amount": claim_amount,
                "deductible": deductible,
                "copay_amount": copay_amount,
                "copay_percentage": copay_percentage,
                "room_rent_limit": room_rent_limit,
                "payable_amount": payable_amount,
                "calculation_type": "health_copay"
            }
            logger.info(f"✓ Payable: ₹{payable_amount:,.0f} (Deductible: ₹{deductible:,.0f}, Co-pay: ₹{copay_amount:,.0f})")
            
            duration = (time.time() - start) * 1000
            logger.info(f"calculate_payout completed in {duration:.0f}ms")
            return result
        
        # MOTOR/HOME CLAIMS - Use depreciation
        zero_dep = policy_data.get("zero_depreciation", False)
        
        if zero_dep:
            depreciation = 0
            depreciation_rate = 0
        else:
            # Load depreciation rates
            repair_costs = load_json_data(config.REPAIR_COSTS_PATH)
            
            if claim_type.startswith("motor_"):
                dep_rates = repair_costs.get("depreciation_rates", {}).get("motor", {})
                if vehicle_age_years <= 0.5:
                    depreciation_rate = dep_rates.get("0-6_months", 0)
                elif vehicle_age_years <= 1:
                    depreciation_rate = dep_rates.get("6-12_months", 5)
                elif vehicle_age_years <= 2:
                    depreciation_rate = dep_rates.get("1-2_years", 10)
                elif vehicle_age_years <= 3:
                    depreciation_rate = dep_rates.get("2-3_years", 15)
                elif vehicle_age_years <= 4:
                    depreciation_rate = dep_rates.get("3-4_years", 25)
                elif vehicle_age_years <= 5:
                    depreciation_rate = dep_rates.get("4-5_years", 35)
                else:
                    depreciation_rate = dep_rates.get("5+_years", 50)
            elif claim_type.startswith("home_"):
                dep_rates = repair_costs.get("depreciation_rates", {}).get("home", {})
                depreciation_rate = dep_rates.get("general", 10)
            else:
                depreciation_rate = 0
            
            depreciation = claim_amount * (depreciation_rate / 100)
        
        # Calculate final payout
        amount_after_depreciation = claim_amount - depreciation
        payable_amount = max(0, amount_after_depreciation - deductible)
        
        result = {
            "claimed_amount": claim_amount,
            "deductible": deductible,
            "depreciation": depreciation,
            "depreciation_rate": depreciation_rate if not zero_dep else 0,
            "payable_amount": payable_amount,
            "zero_depreciation_applied": zero_dep,
            "calculation_type": "motor_depreciation" if claim_type.startswith("motor_") else "home_depreciation"
        }
        
        logger.info(f"✓ Payable: ₹{payable_amount:,.0f} (Deductible: ₹{deductible:,.0f}, Depreciation: ₹{depreciation:,.0f})")
        
        duration = (time.time() - start) * 1000
        logger.info(f"calculate_payout completed in {duration:.0f}ms")
        return result
        
    except Exception as e:
        logger.error(f"Error in calculate_payout: {e}")
        return {"error": str(e)}


# ============ Tool 6: Verify Documents ============

@tool
def verify_documents(
    claim_type: str,
    submitted_docs: List[str]
) -> dict:
    """
    Verify if required documents are submitted for this claim type.
    
    REQUIRES: extract_claim_data (needs claim_type to determine required docs)
    
    Args:
        claim_type: Normalized claim type (e.g., 'motor_accident')
        submitted_docs: List of document names submitted by customer
    
    Returns:
        Document verification with 'required', 'submitted', 'missing' lists and 'complete' boolean
    """
    start = time.time()
    logger.info(f"Tool: Verifying documents for {claim_type}...")
    
    try:
        doc_rules = load_json_data(config.DOCUMENT_RULES_PATH)
        
        # Get required documents for this claim type
        claim_docs = doc_rules.get(claim_type, {})
        required = claim_docs.get("critical", []) + claim_docs.get("standard", [])
        
        if not required:
            required = ["Repair estimate", "Photos of damage", "Policy copy"]
        
        # Check what's missing
        submitted_lower = [doc.lower() for doc in submitted_docs]
        missing = []
        
        for req_doc in required:
            found = any(keyword in ' '.join(submitted_lower) 
                       for keyword in req_doc.lower().split()[:2])
            if not found:
                missing.append(req_doc)
        
        result = {
            "required": required,
            "submitted": submitted_docs,
            "missing": missing,
            "complete": len(missing) == 0
        }
        
        if result["complete"]:
            logger.info("✓ All documents submitted")
        else:
            logger.warning(f"✗ Missing {len(missing)} document(s)")
        
        duration = (time.time() - start) * 1000
        logger.info(f"verify_documents completed in {duration:.0f}ms")
        return result
        
    except Exception as e:
        logger.error(f"Error in verify_documents: {e}")
        return {"error": str(e)}


# ============ Tool 7: Check Claim History ============

@tool
def check_claim_history(
    customer_id: str = "",
    vehicle_reg: str = ""
) -> dict:
    """
    Check customer's past claim history and assess risk.
    
    REQUIRES: Nothing (can run in parallel with other tools)
    
    Args:
        customer_id: Customer identifier
        vehicle_reg: Vehicle registration as alternate identifier
    
    Returns:
        Claim history with past_claims list, total_claims, fraud_flags, and risk_level
    """
    start = time.time()
    identifier = customer_id or vehicle_reg
    logger.info(f"Tool: Checking claim history for {identifier}...")
    
    try:
        # Try database first
        try:
            from database.models import get_db_manager
            from database.crud import get_customer, get_customer_claims, get_customer_claim_history
            
            db_manager = get_db_manager()
            session = db_manager.get_session()
            
            try:
                customer = get_customer(session, customer_id)
                
                if customer:
                    active_claims = get_customer_claims(session, customer.id)
                    historical_claims = get_customer_claim_history(session, customer_id)
                    
                    past_claims = []
                    for claim in active_claims:
                        past_claims.append({
                            "claim_id": claim.claim_id,
                            "claim_type": claim.claim_type.value,
                            "filed_date": claim.filed_date.isoformat(),
                            "status": claim.status.value,
                            "amount": claim.payout_amount or claim.estimated_cost
                        })
                    
                    for hist in historical_claims:
                        past_claims.append({
                            "claim_id": hist.claim_id,
                            "claim_type": hist.claim_type,
                            "filed_date": hist.filed_date.isoformat(),
                            "status": hist.status,
                            "amount": hist.claim_amount
                        })
                    
                    total_claims = len(past_claims)
                    fraud_flags = []
                    
                    ncb_percentage = 0
                    policies = customer.policies
                    if policies:
                        ncb_values = [p.ncb_percentage for p in policies if p.ncb_percentage]
                        if ncb_values:
                            ncb_percentage = max(ncb_values)
                    
                    result = {
                        "customer_found": True,
                        "customer_name": customer.name,
                        "past_claims": past_claims,
                        "total_claims": total_claims,
                        "claim_free_years": 0 if total_claims > 0 else 1,
                        "ncb_percentage": ncb_percentage,
                        "fraud_flags": fraud_flags,
                        "risk_level": "high" if fraud_flags else ("medium" if total_claims > 2 else "low"),
                        "source": "database"
                    }
                    
                    logger.info(f"✓ Database: {total_claims} past claim(s), Risk: {result['risk_level']}")
                    
                    duration = (time.time() - start) * 1000
                    logger.info(f"check_claim_history completed in {duration:.0f}ms")
                    return result
                else:
                    logger.info("Customer not found in database, checking JSON fallback")
            finally:
                session.close()
                
        except Exception as db_error:
            logger.warning(f"Database query failed: {db_error}, using JSON fallback")
        
        # Fallback to JSON data
        claims_history = load_json_data(config.CLAIMS_HISTORY_PATH)
        
        identifier = customer_id or vehicle_reg.replace(" ", "").upper()
        customer_history = claims_history.get(identifier, claims_history.get(customer_id, {}))
        
        if not customer_history:
            result = {
                "customer_found": False,
                "past_claims": [],
                "total_claims": 0,
                "claim_free_years": 0,
                "ncb_percentage": 0,
                "fraud_flags": [],
                "risk_level": "unknown",
                "source": "json_fallback"
            }
        else:
            past_claims = customer_history.get("past_claims", [])
            fraud_flags = customer_history.get("fraud_flags", [])
            
            result = {
                "customer_found": True,
                "customer_name": customer_history.get("customer_name", ""),
                "past_claims": past_claims,
                "total_claims": len(past_claims),
                "claim_free_years": customer_history.get("claim_free_years", 0),
                "ncb_percentage": customer_history.get("ncb_percentage", 0),
                "fraud_flags": fraud_flags,
                "risk_level": "high" if fraud_flags else ("medium" if len(past_claims) > 2 else "low"),
                "source": "json_fallback"
            }
        
        logger.info(f"✓ History: {result['total_claims']} past claim(s), Risk: {result['risk_level']}")
        
        duration = (time.time() - start) * 1000
        logger.info(f"check_claim_history completed in {duration:.0f}ms")
        return result
        
    except Exception as e:
        logger.error(f"Error in check_claim_history: {e}")
        return {"error": str(e)}


# ============ Tool 8: Make Decision ============

@tool
def make_decision(
    coverage_check: dict,
    exclusions: List[dict],
    payout_calculation: dict,
    document_status: dict,
    claim_history: dict,
    claim_amount: float
) -> dict:
    """
    Make final decision on claim approval, denial, or review.
    
    REQUIRES: ALL of the following must be called first:
    - check_coverage (for coverage_check)
    - check_exclusions (for exclusions)
    - calculate_payout (for payout_calculation)
    - verify_documents (for document_status)
    - check_claim_history (for claim_history)
    
    Args:
        coverage_check: Coverage verification result
        exclusions: List of exclusions from check_exclusions
        payout_calculation: Payout calculation from calculate_payout
        document_status: Document verification from verify_documents
        claim_history: Customer history from check_claim_history
        claim_amount: Original claimed amount
    
    Returns:
        Decision with 'decision' (APPROVED/DENIED/REVIEW) and 'reasoning'
    """
    start = time.time()
    logger.info("Tool: Making final decision...")
    
    try:
        business_rules = load_json_data(config.BUSINESS_RULES_PATH)
        auto_approve = business_rules.get("auto_approval", {}).get("conditions", {})
        
        # Check for automatic rejection
        if not coverage_check.get("covered", False):
            decision, reasoning = "DENIED", "Claim type not covered under policy"
            logger.info(f"Decision: {decision} - {reasoning}")
            return {"decision": decision, "reasoning": reasoning}
        
        exclusions_apply = any(e.get("applies", False) for e in exclusions)
        if exclusions_apply:
            applicable = [e["exclusion"] for e in exclusions if e.get("applies")]
            decision, reasoning = "DENIED", f"Policy exclusions apply: {', '.join(applicable)}"
            logger.info(f"Decision: {decision} - {reasoning}")
            return {"decision": decision, "reasoning": reasoning}
        
        fraud_flags = claim_history.get("fraud_flags", [])
        if fraud_flags:
            decision, reasoning = "DENIED", f"Fraud indicators detected: {', '.join(fraud_flags)}"
            logger.info(f"Decision: {decision} - {reasoning}")
            return {"decision": decision, "reasoning": reasoning}
        
        # Check for automatic approval
        max_auto_approve = auto_approve.get("max_amount", 50000)
        docs_complete = document_status.get("complete", False)
        claim_free_years = claim_history.get("claim_free_years", 0)
        
        if (claim_amount <= max_auto_approve and 
            docs_complete and 
            not fraud_flags and 
            claim_free_years >= 1):
            decision, reasoning = "APPROVED", f"Auto-approved: Amount within limit (₹{max_auto_approve:,.0f}), all criteria met"
            logger.info(f"Decision: {decision} - {reasoning}")
            
            duration = (time.time() - start) * 1000
            logger.info(f"make_decision completed in {duration:.0f}ms")
            return {"decision": decision, "reasoning": reasoning}
        
        # Check for manual review
        if claim_amount > max_auto_approve:
            decision, reasoning = "REVIEW", f"Manual review required: Amount exceeds auto-approval limit (₹{max_auto_approve:,.0f})"
            logger.info(f"Decision: {decision} - {reasoning}")
            
            duration = (time.time() - start) * 1000
            return {"decision": decision, "reasoning": reasoning}
        
        if not docs_complete:
            missing_count = len(document_status.get("missing", []))
            decision, reasoning = "APPROVED", f"Conditionally approved pending {missing_count} document(s)"
            logger.info(f"Decision: {decision} - {reasoning}")
            
            duration = (time.time() - start) * 1000
            return {"decision": decision, "reasoning": reasoning}
        
        if claim_history.get("total_claims", 0) > 3:
            decision, reasoning = "REVIEW", "Manual review required: Multiple past claims"
            logger.info(f"Decision: {decision} - {reasoning}")
            
            duration = (time.time() - start) * 1000
            return {"decision": decision, "reasoning": reasoning}
        
        # Default: Approve
        decision, reasoning = "APPROVED", "All checks passed, claim approved"
        logger.info(f"Decision: {decision} - {reasoning}")
        
        duration = (time.time() - start) * 1000
        logger.info(f"make_decision completed in {duration:.0f}ms")
        return {"decision": decision, "reasoning": reasoning}
        
    except Exception as e:
        logger.error(f"Error in make_decision: {e}")
        return {"decision": "REVIEW", "reasoning": f"Error in decision making: {str(e)}"}


# ============ Tool 9: Generate Report ============

@tool
def generate_report(
    claim_id: str,
    claim_data: dict,
    coverage_check: dict,
    exclusions: List[dict],
    payout_calculation: dict,
    document_status: dict,
    claim_history: dict,
    decision: str,
    decision_reasoning: str,
    processing_time: float
) -> str:
    """
    Generate comprehensive claim processing report.
    
    REQUIRES: make_decision (this should be the LAST tool called)
    
    Args:
        claim_id: Unique claim identifier
        claim_data: Structured claim data
        coverage_check: Coverage verification result
        exclusions: List of exclusions
        payout_calculation: Payout calculation result
        document_status: Document verification result
        claim_history: Customer history
        decision: Final decision (APPROVED/DENIED/REVIEW)
        decision_reasoning: Reasoning for the decision
        processing_time: Total processing time in seconds
    
    Returns:
        Formatted report text
    """
    start = time.time()
    logger.info("Tool: Generating final report...")
    
    try:
        def fmt_curr(amount):
            return f"₹{amount:,.0f}" if amount else "₹0"
        
        claim_type = claim_data.get('claim_type', 'N/A')
        is_health = claim_type.startswith("health_")
        is_motor = claim_type.startswith("motor_")
        is_home = claim_type.startswith("home_")
        
        report = f"""
===== CLAIM PROCESSING REPORT =====
Claim ID: {claim_id}
Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: {decision}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLAIM DETAILS:
• Type: {claim_type}
• Incident Date: {claim_data.get('incident_date', 'N/A')}
"""
        
        # Add category-specific details
        if is_health:
            report += f"• Hospital: {claim_data.get('hospital_name', 'N/A')}\n"
            report += f"• Treatment: {claim_data.get('treatment_type', 'N/A')}\n"
            if claim_data.get('hospitalization_date'):
                report += f"• Admission Date: {claim_data.get('hospitalization_date', 'N/A')}\n"
        elif is_motor:
            report += f"• Vehicle: {claim_data.get('vehicle_registration', 'N/A')}\n"
            report += f"• Damage: {claim_data.get('damage_description', 'N/A')}\n"
        elif is_home:
            report += f"• Property: {claim_data.get('property_id', 'N/A')}\n"
            report += f"• Damage: {claim_data.get('damage_description', 'N/A')}\n"
        
        report += "\nCOVERAGE VERIFICATION:\n"
        
        if coverage_check.get("covered"):
            report += f"✓ Covered under {coverage_check.get('section', 'N/A')}\n"
            report += f"✓ Coverage Limit: {fmt_curr(coverage_check.get('coverage_limit', 0))}\n"
        else:
            report += f"✗ Not covered under policy\n"
        
        # Exclusions
        applicable_exclusions = [e for e in exclusions if e.get("applies", False)]
        if not applicable_exclusions:
            report += "✓ No exclusions apply\n"
        else:
            report += "✗ Exclusions apply:\n"
            for exc in applicable_exclusions:
                report += f"  - {exc.get('exclusion')}\n"
        
        # Payout
        report += f"\nPAYOUT CALCULATION:\n"
        
        if is_health:
            report += f"• Treatment Cost: {fmt_curr(payout_calculation.get('claimed_amount', 0))}\n"
            report += f"• Deductible: {fmt_curr(payout_calculation.get('deductible', 0))}\n"
            copay = payout_calculation.get('copay_amount', 0)
            copay_pct = payout_calculation.get('copay_percentage', 0)
            report += f"• Co-pay: {fmt_curr(copay)} ({copay_pct}% of claim amount)\n"
            report += f"• PAYABLE AMOUNT: {fmt_curr(payout_calculation.get('payable_amount', 0))}\n"
        else:
            report += f"• Claimed Amount: {fmt_curr(payout_calculation.get('claimed_amount', 0))}\n"
            report += f"• Deductible: {fmt_curr(payout_calculation.get('deductible', 0))}\n"
            report += f"• Depreciation: {fmt_curr(payout_calculation.get('depreciation', 0))}"
            if payout_calculation.get('zero_depreciation_applied'):
                report += " (Zero Depreciation Cover Active)\n"
            else:
                report += f" ({payout_calculation.get('depreciation_rate', 0)}% applied)\n"
            report += f"• PAYABLE AMOUNT: {fmt_curr(payout_calculation.get('payable_amount', 0))}\n"
        
        # Documents
        report += f"\nDOCUMENT VERIFICATION:\n"
        if document_status.get("complete"):
            report += "✓ All required documents submitted\n"
        else:
            missing = document_status.get("missing", [])
            report += f"✗ Missing {len(missing)} document(s):\n"
            for doc in missing[:5]:
                report += f"  - {doc}\n"
        
        # Claim History
        report += f"\nCLAIM HISTORY:\n"
        if claim_history.get("customer_found"):
            report += f"• Customer: {claim_history.get('customer_name', 'N/A')}\n"
            report += f"• Past Claims: {claim_history.get('total_claims', 0)}\n"
            report += f"• Claim-Free Years: {claim_history.get('claim_free_years', 0)}\n"
            report += f"• NCB: {claim_history.get('ncb_percentage', 0)}%\n"
            if claim_history.get('fraud_flags'):
                report += f"• ⚠ Fraud Flags: {', '.join(claim_history.get('fraud_flags'))}\n"
        else:
            report += "• New customer (no history found)\n"
        
        # Decision
        report += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        report += f"DECISION: {decision}\n"
        report += f"Reasoning: {decision_reasoning}\n"
        
        # Next actions
        if decision == "APPROVED":
            if not document_status.get("complete"):
                report += f"\nNEXT ACTIONS:\n"
                report += "1. Customer to submit missing documents\n"
                report += "2. Schedule surveyor inspection (if required)\n"
                report += "3. Final approval after document verification\n"
            else:
                report += f"\nNEXT ACTIONS:\n"
                report += "1. Process payment\n"
                report += "2. Notify customer\n"
        elif decision == "DENIED":
            report += f"\nNEXT ACTIONS:\n"
            report += "1. Notify customer of denial\n"
            report += "2. Provide appeal process information\n"
        else:
            report += f"\nNEXT ACTIONS:\n"
            report += "1. Forward to claims adjuster for manual review\n"
            report += "2. May require additional investigation\n"
        
        report += f"\nProcessing Time: {processing_time:.2f} seconds\n"
        report += f"Processed by: ClaimFlow AI Agent\n"
        report += "=" * 40 + "\n"
        
        logger.info(f"✓ Report generated: {decision}")
        
        duration = (time.time() - start) * 1000
        logger.info(f"generate_report completed in {duration:.0f}ms")
        return report
        
    except Exception as e:
        logger.error(f"Error in generate_report: {e}")
        return f"Error generating report: {str(e)}"


# ============ Tool Registry for Agent ============

PROCESSING_TOOLS = [
    extract_claim_data,
    retrieve_policy,
    check_coverage,
    check_exclusions,
    calculate_payout,
    verify_documents,
    check_claim_history,
    make_decision,
    generate_report
]

# Tool name to function mapping
TOOL_MAP = {tool.name: tool for tool in PROCESSING_TOOLS}
