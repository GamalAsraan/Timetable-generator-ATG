#!/usr/bin/env python3
"""
Test script to verify the new project structure works correctly.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

def test_imports():
    """Test that all modules can be imported correctly."""
    print("Testing imports...")
    
    try:
        # Test config
        from config import FILE_PATHS, SOLVER_CONFIG
        print("✓ Config imported successfully")
        
        # Test models
        from src.models import Course, Room, Instructor, TimeSlot, Section, AvailableCourse
        print("✓ Models imported successfully")
        
        # Test data loader
        from src.data_loader import DataLoader, DataValidator
        print("✓ Data loader imported successfully")
        
        # Test CSP modules
        from src.csp import ClassSession, VariableGenerator, Domain, DomainBuilder, TimetableState, Assignment
        print("✓ CSP modules imported successfully")
        
        # Test solvers
        from src.solvers import BacktrackingSolver, IterativeSolver, CostEvaluator
        print("✓ Solvers imported successfully")
        
        # Test utils
        from src.utils import save_solution_to_csv, setup_logger
        print("✓ Utils imported successfully")
        
        # Test UI
        from src.ui import CLIInterface
        print("✓ UI imported successfully")
        
        print("\n🎉 All imports successful! The project structure is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_data_loading():
    """Test that data can be loaded from the new structure."""
    print("\nTesting data loading...")
    
    try:
        from src.data_loader import DataLoader
        from config import FILE_PATHS
        
        # Check if data files exist
        import os
        for key, path in FILE_PATHS.items():
            if os.path.exists(path):
                print(f"✓ {key}: {path}")
            else:
                print(f"❌ {key}: {path} (file not found)")
                return False
        
        print("✓ All data files found")
        return True
        
    except Exception as e:
        print(f"❌ Data loading test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Testing Intelligent Timetable CSP Structure")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test data loading
    if not test_data_loading():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The project structure is ready to use.")
        print("\nTo run the timetable generator:")
        print("  python main.py")
        print("\nTo run with custom parameters:")
        print("  python main.py --max-capacity 100 --iterations 50000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
