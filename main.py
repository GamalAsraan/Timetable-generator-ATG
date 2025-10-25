"""
Main entry point for the Intelligent Timetable CSP system.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import FILE_PATHS, OUTPUT_PATHS, SOLVER_CONFIG
from src.data_loader import DataLoader, DataValidator
from src.csp import VariableGenerator, DomainBuilder
from src.solvers import BacktrackingSolver, IterativeSolver, CostEvaluator
from src.utils import save_solution_to_csv, setup_logger, save_optimization_report


def main():
    """Main execution function."""
    # Setup logging
    logger = setup_logger("main")
    logger.info("Starting Intelligent Timetable CSP System")
    
    try:
        # --- 1. Load Data ---
        logger.info("Loading data from files...")
        loader = DataLoader(FILE_PATHS)
        model_data = loader.load_all()
        
        if not model_data:
            logger.error("Failed to load data. Exiting.")
            return False
        
        # Validate data
        validator = DataValidator()
        is_valid, errors, warnings = validator.validate_all(model_data)
        
        if warnings:
            for warning in warnings:
                logger.warning(warning)
        
        if not is_valid:
            logger.error("Data validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("Data loaded and validated successfully")
        
        # --- 2. Generate Variables ---
        logger.info("Generating CSP variables...")
        var_generator = VariableGenerator(model_data, SOLVER_CONFIG['max_group_capacity'])
        all_variables = var_generator.generate_all_variables()
        
        if not all_variables:
            logger.error("No variables generated. Exiting.")
            return False
        
        logger.info(f"Generated {len(all_variables)} variables")
        
        # --- 3. Build Domains ---
        logger.info("Building domains for variables...")
        domain_builder = DomainBuilder(model_data)
        domain_builder.build_all_domains(all_variables)
        
        # Check for unsolvable variables
        unsolvable_vars = [v for v in all_variables if not v.domain.timeslot_sequences or 
                          not v.domain.rooms or not v.domain.instructors]
        
        if unsolvable_vars:
            logger.error(f"Found {len(unsolvable_vars)} unsolvable variables. Problem may be infeasible.")
            return False
        
        logger.info("All variables have valid domains")
        
        # --- 4. Run Phase 1 Solver ---
        logger.info("Starting Phase 1: Backtracking Solver")
        solver = BacktrackingSolver(all_variables, model_data)
        phase1_solution, phase1_state = solver.solve()
        
        if not phase1_solution:
            logger.error("Phase 1 solver failed to find a solution")
            return False
        
        logger.info(f"Phase 1 completed successfully with {len(phase1_solution)} assignments")
        
        # --- 5. Run Phase 2 Optimizer ---
        logger.info("Starting Phase 2: Iterative Optimizer")
        evaluator = CostEvaluator(model_data)
        initial_cost = evaluator.calculate_total_cost(phase1_solution, phase1_state)
        logger.info(f"Initial solution cost: {initial_cost}")
        
        optimizer = IterativeSolver(
            phase1_solution, 
            phase1_state, 
            evaluator, 
            model_data,
            iterations=SOLVER_CONFIG['optimization_iterations']
        )
        
        final_solution = optimizer.optimize()
        final_cost = evaluator.calculate_total_cost(final_solution, optimizer.current_state)
        
        logger.info(f"Phase 2 completed. Final cost: {final_cost}")
        logger.info(f"Improvement: {initial_cost - final_cost} ({(initial_cost - final_cost) / initial_cost * 100:.2f}%)")
        
        # --- 6. Save Results ---
        logger.info("Saving results...")
        
        # Save timetable
        if save_solution_to_csv(final_solution, model_data):
            logger.info("Timetable saved successfully")
        else:
            logger.error("Failed to save timetable")
            return False
        
        # Save optimization report
        save_optimization_report(
            final_solution, 
            initial_cost, 
            final_cost, 
            SOLVER_CONFIG['optimization_iterations']
        )
        
        logger.info("Timetable generation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
