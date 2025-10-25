"""
Timetable visualization utilities.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


class TimetableVisualizer:
    """Create visualizations for timetable data."""
    
    def __init__(self, timetable_df):
        self.df = timetable_df
    
    def create_schedule_heatmap(self, output_file=None):
        """Create a heatmap of the weekly schedule."""
        # Convert time strings to datetime for sorting
        self.df['StartTime_dt'] = pd.to_datetime(self.df['StartTime'], format='%H:%M')
        self.df['EndTime_dt'] = pd.to_datetime(self.df['EndTime'], format='%H:%M')
        
        # Create a pivot table for the heatmap
        pivot_data = []
        for _, row in self.df.iterrows():
            pivot_data.append({
                'Day': row['Day'],
                'Time': row['StartTime'],
                'Course': f"{row['CourseID']} ({row['Type']})",
                'Room': row['Room'],
                'Instructor': row['Instructor']
            })
        
        pivot_df = pd.DataFrame(pivot_data)
        
        # Create the heatmap
        plt.figure(figsize=(12, 8))
        pivot_table = pivot_df.pivot_table(
            index='Time', 
            columns='Day', 
            values='Course', 
            aggfunc=lambda x: ' | '.join(x)
        )
        
        sns.heatmap(
            pivot_table.notna(), 
            cmap='YlOrRd', 
            cbar_kws={'label': 'Scheduled'}
        )
        
        plt.title('Weekly Timetable Schedule')
        plt.xlabel('Day')
        plt.ylabel('Time')
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def create_room_utilization(self, output_file=None):
        """Create room utilization chart."""
        room_usage = self.df.groupby('Room').size().sort_values(ascending=True)
        
        plt.figure(figsize=(10, 6))
        room_usage.plot(kind='barh')
        plt.title('Room Utilization')
        plt.xlabel('Number of Sessions')
        plt.ylabel('Room')
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def create_instructor_workload(self, output_file=None):
        """Create instructor workload chart."""
        instructor_workload = self.df.groupby('Instructor').size().sort_values(ascending=True)
        
        plt.figure(figsize=(10, 6))
        instructor_workload.plot(kind='barh')
        plt.title('Instructor Workload')
        plt.xlabel('Number of Sessions')
        plt.ylabel('Instructor')
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def create_course_distribution(self, output_file=None):
        """Create course type distribution pie chart."""
        course_types = self.df['Type'].value_counts()
        
        plt.figure(figsize=(8, 8))
        plt.pie(course_types.values, labels=course_types.index, autopct='%1.1f%%')
        plt.title('Course Type Distribution')
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def generate_summary_report(self, output_file=None):
        """Generate a comprehensive summary report."""
        report = f"""
Timetable Summary Report
========================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Basic Statistics:
- Total Sessions: {len(self.df)}
- Unique Courses: {self.df['CourseID'].nunique()}
- Unique Instructors: {self.df['Instructor'].nunique()}
- Unique Rooms: {self.df['Room'].nunique()}
- Unique Sections: {self.df['Sections'].nunique()}

Course Type Distribution:
{self.df['Type'].value_counts().to_string()}

Room Utilization (Top 10):
{self.df['Room'].value_counts().head(10).to_string()}

Instructor Workload (Top 10):
{self.df['Instructor'].value_counts().head(10).to_string()}

Daily Distribution:
{self.df['Day'].value_counts().to_string()}
"""
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Summary report saved to {output_file}")
        else:
            print(report)
        
        return report
