"""
Command-line interface for the timetable system.
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from config import FILE_PATHS, OUTPUT_PATHS, SOLVER_CONFIG


class CLIInterface:
    """Command-line interface for the timetable generator."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self):
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="Intelligent Timetable CSP Generator",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python main.py                          # Run with default settings
  python main.py --max-capacity 100       # Set max group capacity
  python main.py --iterations 50000      # Set optimization iterations
  python main.py --output custom.csv     # Custom output file
            """
        )
        
        parser.add_argument(
            '--max-capacity',
            type=int,
            default=SOLVER_CONFIG['max_group_capacity'],
            help=f'Maximum group capacity (default: {SOLVER_CONFIG["max_group_capacity"]})'
        )
        
        parser.add_argument(
            '--iterations',
            type=int,
            default=SOLVER_CONFIG['optimization_iterations'],
            help=f'Number of optimization iterations (default: {SOLVER_CONFIG["optimization_iterations"]})'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            default=OUTPUT_PATHS['timetable'],
            help=f'Output file path (default: {OUTPUT_PATHS["timetable"]})'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Only validate data without generating timetable'
        )
        
        return parser
    
    def run(self, args=None):
        """Run the CLI interface."""
        if args is None:
            args = self.parser.parse_args()
        
        # Update configuration based on arguments
        if args.max_capacity:
            SOLVER_CONFIG['max_group_capacity'] = args.max_capacity
        
        if args.iterations:
            SOLVER_CONFIG['optimization_iterations'] = args.iterations
        
        if args.output:
            OUTPUT_PATHS['timetable'] = args.output
        
        # Import and run main function
        from main import main
        
        if args.validate_only:
            print("Running data validation only...")
            # TODO: Implement validation-only mode
            return main()
        else:
            return main()
