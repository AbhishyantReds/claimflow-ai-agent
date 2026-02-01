"""
Configuration settings for ClaimFlow AI
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Insurance RAG System
INSURANCE_RAG_URL = os.getenv("INSURANCE_RAG_URL", "http://localhost:8000")

# Application Settings
MAX_CONVERSATION_TURNS = int(os.getenv("MAX_CONVERSATION_TURNS", "10"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Supported claim types
CLAIM_TYPES = {
    "motor": ["motor_accident", "motor_theft", "motor_fire", "motor_vandalism"],
    "home": ["home_fire", "home_theft", "home_flood", "home_earthquake", "home_storm"],
    "health": ["health_accident", "health_hospitalization", "health_surgery", "health_critical_illness"]
}

# Required fields for claim processing
REQUIRED_FIELDS = {
    "claim_type": {
        "description": "Type of claim (auto-detected from description)",
        "prompt": "What type of insurance claim is this?"
    },
    
    # Universal fields
    "incident_date": {
        "description": "Date when the incident occurred",
        "prompt": "When did this incident occur?",
        "required_for": "all"
    },
    "customer_id": {
        "description": "Customer identification or policy number",
        "prompt": "What is your customer ID or policy number?",
        "required_for": "all",
        "optional": True
    },
    
    # Motor claim specific fields
    "damage_description": {
        "description": "Detailed description of the damage",
        "prompt": "Can you describe the damage in detail?",
        "required_for": ["motor_accident", "motor_theft", "motor_fire", "motor_vandalism", 
                        "home_fire", "home_theft", "home_flood", "home_earthquake", "home_storm"]
    },
    "vehicle_registration": {
        "description": "Vehicle registration number",
        "prompt": "What is your vehicle registration number?",
        "required_for": ["motor_accident", "motor_theft", "motor_fire", "motor_vandalism"]
    },
    "repair_estimate": {
        "description": "Estimated repair cost amount",
        "prompt": "Do you have a repair estimate? If so, what is the amount?",
        "required_for": ["motor_accident", "motor_fire", "motor_vandalism",
                        "home_fire", "home_flood", "home_earthquake", "home_storm"]
    },
    
    # Home claim specific fields
    "property_id": {
        "description": "Property address or identification",
        "prompt": "Can you provide your property address?",
        "required_for": ["home_fire", "home_theft", "home_flood", "home_earthquake", "home_storm"]
    },
    
    # Health claim specific fields
    "hospital_name": {
        "description": "Name of the hospital where treatment was received",
        "prompt": "Which hospital were you admitted to?",
        "required_for": ["health_accident", "health_hospitalization", "health_surgery", "health_critical_illness"]
    },
    "treatment_type": {
        "description": "Type of medical treatment or diagnosis",
        "prompt": "What was the diagnosis or type of treatment?",
        "required_for": ["health_accident", "health_hospitalization", "health_surgery", "health_critical_illness"]
    },
    "hospitalization_date": {
        "description": "Date of hospital admission",
        "prompt": "When were you admitted to the hospital?",
        "required_for": ["health_hospitalization", "health_surgery", "health_critical_illness"]
    },
    "treatment_cost": {
        "description": "Total treatment cost estimate",
        "prompt": "What is the estimated or actual treatment cost?",
        "required_for": ["health_accident", "health_hospitalization", "health_surgery", "health_critical_illness"]
    },
    "medical_bills": {
        "description": "Medical bills and prescription availability",
        "prompt": "Do you have the hospital bills and medical reports?",
        "required_for": ["health_accident", "health_hospitalization", "health_surgery", "health_critical_illness"],
        "optional": True
    }
}

# Model Configuration
MODEL_NAME = "gpt-4o"
MODEL_TEMPERATURE = 0.7

# File paths for mock data
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CLAIMS_HISTORY_PATH = os.path.join(DATA_DIR, "claims_history.json")
REPAIR_COSTS_PATH = os.path.join(DATA_DIR, "repair_costs.json")
BUSINESS_RULES_PATH = os.path.join(DATA_DIR, "business_rules.json")
DOCUMENT_RULES_PATH = os.path.join(DATA_DIR, "document_rules.json")

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": LOG_LEVEL
        }
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console"]
    }
}
