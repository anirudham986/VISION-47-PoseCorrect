"""
Exercise Biomechanics Database
Based on NSCA/ACSM standards
"""

EXERCISE_BIOMECHANICS = {
    "cable_chest_fly": {
        "description": "Chest isolation exercise using cable machine",
        "key_joints": ["elbow", "shoulder"],
        "ideal_angles": {
            "elbow": {
                "range": (150, 170),
                "ideal": 160,
                "measurement_notes": "Elbow should remain slightly bent throughout movement",
                "critical": False
            },
            "shoulder_adduction": {
                "range": (0, 30),
                "ideal": 15,
                "measurement_notes": "Arms brought together in front of chest",
                "critical": False
            }
        },
        "common_errors": {
            "elbow_locked": {
                "threshold": 175,
                "message": "Don't lock elbows, keep slight bend",
                "severity": "warning"
            },
            "elbow_too_bent": {
                "threshold": 150,
                "message": "Elbows too bent, reduce angle",
                "severity": "warning"
            },
            "excessive_range": {
                "threshold": 35,
                "message": "Arms going too far back, risk shoulder injury",
                "severity": "danger"
            }
        },
        "camera_angle": "front",
        "reps_phase": "peak_contraction"
    },
    
    "lunges": {
        "description": "Unilateral lower body exercise",
        "key_joints": ["front_knee", "front_hip", "rear_knee", "torso"],
        "ideal_angles": {
            "front_knee": {
                "range": (80, 100),
                "ideal": 90,
                "measurement_notes": "Knee should be directly above ankle",
                "critical": True
            },
            "front_hip": {
                "range": (80, 100),
                "ideal": 90,
                "measurement_notes": "Thigh parallel to floor",
                "critical": False
            },
            "rear_knee": {
                "range": (80, 100),
                "ideal": 90,
                "measurement_notes": "Knee should hover just above floor",
                "critical": False
            },
            "torso": {
                "range": (85, 100),
                "ideal": 90,
                "measurement_notes": "Torso nearly vertical, minimal forward lean",
                "critical": True
            }
        },
        "common_errors": {
            "knee_past_toes": {
                "threshold": 100,
                "message": "Front knee passing toes, shift weight back",
                "severity": "danger"
            },
            "torso_lean": {
                "threshold": 85,
                "message": "Torso leaning too far forward",
                "severity": "warning"
            },
            "rear_knee_touching": {
                "threshold": 70,
                "message": "Rear knee touching ground, control descent",
                "severity": "warning"
            }
        },
        "camera_angle": "side",
        "reps_phase": "bottom_position"
    },
    
    "deadlift": {
        "description": "Hip hinge compound lift",
        "key_joints": ["knee", "hip", "torso"],
        "ideal_angles": {
            "knee_start": {
                "range": (110, 120),
                "ideal": 115,
                "measurement_notes": "Knees slightly bent, not squatting deeply",
                "critical": True
            },
            "hip_start": {
                "range": (40, 50),
                "ideal": 45,
                "measurement_notes": "Hips high, well above knees",
                "critical": True
            },
            "torso_horizontal": {
                "range": (35, 45),
                "ideal": 40,
                "measurement_notes": "Angle between torso and floor",
                "critical": True
            },
            "spine_angle": {
                "range": (175, 180),
                "ideal": 180,
                "measurement_notes": "Back must be kept straight",
                "critical": True
            }
        },
        "common_errors": {
            "rounded_back": {
                "threshold": 170,
                "message": "BACK ROUNDED! Straighten immediately - INJURY RISK",
                "severity": "critical"
            },
            "hips_too_low": {
                "threshold": 60,
                "message": "Hips too low - you're squatting, not deadlifting",
                "severity": "danger"
            },
            "hips_too_high": {
                "threshold": 30,
                "message": "Hips too high - excessive stress on lower back",
                "severity": "danger"
            }
        },
        "camera_angle": "side",
        "reps_phase": "start_position"
    },
    
    "lat_pulldown": {
        "description": "Upper back compound exercise",
        "key_joints": ["elbow", "shoulder"],
        "ideal_angles": {
            "elbow": {
                "range": (90, 100),
                "ideal": 95,
                "measurement_notes": "Elbows bent at right angle at bottom",
                "critical": False
            },
            "shoulder_adduction": {
                "range": (30, 45),
                "ideal": 37.5,
                "measurement_notes": "Elbow close to side of torso",
                "critical": True
            },
            "torso_lean": {
                "range": (0, 15),
                "ideal": 10,
                "measurement_notes": "Slight back lean, not excessive",
                "critical": False
            }
        },
        "common_errors": {
            "behind_neck": {
                "condition": "wrist_behind_head",
                "message": "Pulling behind neck - DANGEROUS for cervical spine",
                "severity": "critical"
            },
            "excessive_lean": {
                "threshold": 20,
                "message": "Leaning back too much, using momentum",
                "severity": "warning"
            },
            "partial_rom": {
                "threshold": 110,
                "message": "Not full range, bar should reach chest",
                "severity": "warning"
            }
        },
        "camera_angle": "front",
        "reps_phase": "bottom_peak_contraction"
    },
    
    "weighted_squats": {
        "description": "Barbell back squat with weight",
        "key_joints": ["knee", "hip", "torso"],
        "ideal_angles": {
            "knee": {
                "range": (70, 100),
                "ideal": 85,
                "measurement_notes": "Hip crease below knee, 70-90° target",
                "critical": True
            },
            "hip": {
                "range": (45, 75),
                "ideal": 60,
                "measurement_notes": "Related to depth and torso lean",
                "critical": False
            },
            "torso_hip_parallelism": {
                "range": (0, 15),
                "ideal": 10,
                "measurement_notes": "Shin and torso angles should be parallel",
                "critical": True
            },
            "knee_valgus": {
                "range": (0, 10),
                "ideal": 0,
                "measurement_notes": "Knees should not cave inward",
                "critical": True
            }
        },
        "common_errors": {
            "butt_wink": {
                "condition": "pelvic_tilt_at_bottom",
                "message": "Butt wink - lumbar rounding at bottom",
                "severity": "danger"
            },
            "knee_valgus_excessive": {
                "threshold": 15,
                "message": "Knees caving in - ACL injury risk",
                "severity": "critical"
            },
            "forward_lean": {
                "threshold": 30,
                "message": "Excessive forward lean, bar path compromised",
                "severity": "warning"
            },
            "heels_lifting": {
                "condition": "heel_elevation",
                "message": "Heels lifting off ground",
                "severity": "danger"
            }
        },
        "camera_angle": "side",
        "reps_phase": "bottom_position"
    }
}

# Helper functions
def get_exercise_angles(exercise_name):
    """Get ideal angles for specific exercise"""
    if exercise_name not in EXERCISE_BIOMECHANICS:
        raise ValueError(f"Exercise '{exercise_name}' not in database")
    
    return EXERCISE_BIOMECHANICS[exercise_name]["ideal_angles"]

def get_exercise_errors(exercise_name):
    """Get common errors for specific exercise"""
    if exercise_name not in EXERCISE_BIOMECHANICS:
        raise ValueError(f"Exercise '{exercise_name}' not in database")
    
    return EXERCISE_BIOMECHANICS[exercise_name]["common_errors"]

def list_exercises():
    """List all available exercises"""
    return list(EXERCISE_BIOMECHANICS.keys())

def get_exercise_details(exercise_name):
    """Get all details for an exercise"""
    if exercise_name not in EXERCISE_BIOMECHANICS:
        return None
    
    return EXERCISE_BIOMECHANICS[exercise_name]
