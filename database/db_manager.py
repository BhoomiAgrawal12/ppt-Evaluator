import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = "evaluations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Evaluations table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS evaluations (
                    id TEXT PRIMARY KEY,
                    team_name TEXT,
                    problem_statement TEXT,
                    file_name TEXT,
                    timestamp DATETIME,
                    evaluation_data TEXT,
                    final_score REAL,
                    normalized_score REAL,
                    percentage_score REAL,
                    grade TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Problem statements table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS problem_statements (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    category TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Rankings table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS rankings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evaluation_id TEXT,
                    problem_statement_id TEXT,
                    rank INTEGER,
                    ranking_score REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (evaluation_id) REFERENCES evaluations (id)
                )
                ''')
                
                # Component scores table for detailed analysis
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS component_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evaluation_id TEXT,
                    component_name TEXT,
                    raw_score REAL,
                    weighted_score REAL,
                    weight REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (evaluation_id) REFERENCES evaluations (id)
                )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def store_evaluation(self, evaluation_results: Dict[str, Any]) -> str:
        """Store evaluation results in database"""
        try:
            evaluation_id = str(uuid.uuid4())
            
            # Extract key information
            team_name = evaluation_results.get('team_name', '')
            problem_statement = evaluation_results.get('problem_statement', '')
            file_path = evaluation_results.get('file_path', '')
            file_name = os.path.basename(file_path) if file_path else ''
            timestamp = evaluation_results.get('timestamp', datetime.now().isoformat())
            
            # Extract final score information
            final_score_data = evaluation_results.get('final_score', {})
            final_score = final_score_data.get('total_score', 0.0) if isinstance(final_score_data, dict) else 0.0
            normalized_score = final_score_data.get('normalized_score', 0.0) if isinstance(final_score_data, dict) else 0.0
            percentage_score = final_score_data.get('percentage_score', 0.0) if isinstance(final_score_data, dict) else 0.0
            grade = final_score_data.get('grade', '') if isinstance(final_score_data, dict) else ''
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Store main evaluation
                cursor.execute('''
                INSERT INTO evaluations 
                (id, team_name, problem_statement, file_name, timestamp, evaluation_data, 
                 final_score, normalized_score, percentage_score, grade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    evaluation_id,
                    team_name,
                    problem_statement,
                    file_name,
                    timestamp,
                    json.dumps(evaluation_results),
                    final_score,
                    normalized_score,
                    percentage_score,
                    grade
                ))
                
                # Store component scores
                if isinstance(final_score_data, dict) and 'component_scores' in final_score_data:
                    self._store_component_scores(cursor, evaluation_id, final_score_data)
                
                conn.commit()
                logger.info(f"Stored evaluation {evaluation_id} for team {team_name}")
                
            return evaluation_id
            
        except Exception as e:
            logger.error(f"Error storing evaluation: {str(e)}")
            raise
    
    def _store_component_scores(self, cursor, evaluation_id: str, final_score_data: Dict[str, Any]):
        """Store component scores in separate table"""
        try:
            component_scores = final_score_data.get('component_scores', {})
            score_breakdown = final_score_data.get('score_breakdown', {})
            components = score_breakdown.get('components', {})
            
            for component_name, raw_score in component_scores.items():
                component_info = components.get(component_name, {})
                weighted_score = component_info.get('weighted_score', 0.0)
                weight = component_info.get('weight', 0.0)
                
                cursor.execute('''
                INSERT INTO component_scores 
                (evaluation_id, component_name, raw_score, weighted_score, weight)
                VALUES (?, ?, ?, ?, ?)
                ''', (evaluation_id, component_name, raw_score, weighted_score, weight))
                
        except Exception as e:
            logger.error(f"Error storing component scores: {str(e)}")
    
    def get_evaluation(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve evaluation by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT * FROM evaluations WHERE id = ?
                ''', (evaluation_id,))
                
                row = cursor.fetchone()
                
                if row:
                    evaluation = dict(row)
                    # Parse JSON data
                    evaluation['evaluation_data'] = json.loads(evaluation['evaluation_data'])
                    return evaluation
                
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving evaluation {evaluation_id}: {str(e)}")
            return None
    
    def get_all_evaluations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve all evaluations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT * FROM evaluations 
                ORDER BY created_at DESC 
                LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                
                evaluations = []
                for row in rows:
                    evaluation = dict(row)
                    # Don't parse full evaluation_data for list view (performance)
                    # Just include summary information
                    evaluation.pop('evaluation_data', None)
                    evaluations.append(evaluation)
                
                return evaluations
                
        except Exception as e:
            logger.error(f"Error retrieving evaluations: {str(e)}")
            return []
    
    def get_evaluations_by_team(self, team_name: str) -> List[Dict[str, Any]]:
        """Retrieve evaluations for a specific team"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT * FROM evaluations 
                WHERE team_name = ?
                ORDER BY created_at DESC
                ''', (team_name,))
                
                rows = cursor.fetchall()
                
                evaluations = []
                for row in rows:
                    evaluation = dict(row)
                    evaluation.pop('evaluation_data', None)  # Exclude detailed data
                    evaluations.append(evaluation)
                
                return evaluations
                
        except Exception as e:
            logger.error(f"Error retrieving evaluations for team {team_name}: {str(e)}")
            return []
    
    def get_rankings_by_ps(self, problem_statement_text: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get rankings for presentations addressing a specific problem statement"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get evaluations for this problem statement, ordered by score
                cursor.execute('''
                SELECT e.*, cs.raw_score, cs.component_name, cs.weighted_score
                FROM evaluations e
                LEFT JOIN component_scores cs ON e.id = cs.evaluation_id
                WHERE e.problem_statement LIKE ?
                ORDER BY e.percentage_score DESC, e.created_at ASC
                LIMIT ?
                ''', (f"%{problem_statement_text}%", limit))
                
                rows = cursor.fetchall()
                
                # Group by evaluation ID
                evaluations_dict = {}
                for row in rows:
                    eval_id = row['id']
                    if eval_id not in evaluations_dict:
                        evaluations_dict[eval_id] = {
                            'evaluation_id': eval_id,
                            'team_name': row['team_name'],
                            'file_name': row['file_name'],
                            'final_score': row['final_score'],
                            'normalized_score': row['normalized_score'],
                            'percentage_score': row['percentage_score'],
                            'grade': row['grade'],
                            'timestamp': row['timestamp'],
                            'component_scores': {}
                        }
                    
                    if row['component_name']:
                        evaluations_dict[eval_id]['component_scores'][row['component_name']] = {
                            'raw_score': row['raw_score'],
                            'weighted_score': row['weighted_score']
                        }
                
                # Convert to list and add rankings
                ranked_evaluations = list(evaluations_dict.values())
                for i, evaluation in enumerate(ranked_evaluations):
                    evaluation['rank'] = i + 1
                
                return ranked_evaluations
                
        except Exception as e:
            logger.error(f"Error retrieving rankings: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total evaluations
                cursor.execute('SELECT COUNT(*) FROM evaluations')
                stats['total_evaluations'] = cursor.fetchone()[0]
                
                # Average scores
                cursor.execute('SELECT AVG(percentage_score) FROM evaluations WHERE percentage_score > 0')
                avg_score = cursor.fetchone()[0]
                stats['average_score'] = round(avg_score, 2) if avg_score else 0
                
                # Grade distribution
                cursor.execute('''
                SELECT grade, COUNT(*) as count 
                FROM evaluations 
                WHERE grade != '' 
                GROUP BY grade
                ''')
                grade_dist = cursor.fetchall()
                stats['grade_distribution'] = {grade: count for grade, count in grade_dist}
                
                # Top teams
                cursor.execute('''
                SELECT team_name, MAX(percentage_score) as best_score
                FROM evaluations 
                WHERE team_name != '' AND percentage_score > 0
                GROUP BY team_name
                ORDER BY best_score DESC
                LIMIT 10
                ''')
                top_teams = cursor.fetchall()
                stats['top_teams'] = [{'team': team, 'score': score} for team, score in top_teams]
                
                # Component averages
                cursor.execute('''
                SELECT component_name, AVG(raw_score) as avg_score
                FROM component_scores
                GROUP BY component_name
                ''')
                comp_avgs = cursor.fetchall()
                stats['component_averages'] = {comp: round(avg, 3) for comp, avg in comp_avgs}
                
                return stats
                
        except Exception as e:
            logger.error(f"Error retrieving statistics: {str(e)}")
            return {}
    
    def delete_evaluation(self, evaluation_id: str) -> bool:
        """Delete an evaluation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete from component_scores first (foreign key constraint)
                cursor.execute('DELETE FROM component_scores WHERE evaluation_id = ?', (evaluation_id,))
                
                # Delete from rankings
                cursor.execute('DELETE FROM rankings WHERE evaluation_id = ?', (evaluation_id,))
                
                # Delete main evaluation
                cursor.execute('DELETE FROM evaluations WHERE id = ?', (evaluation_id,))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Deleted evaluation {evaluation_id}")
                    return True
                else:
                    logger.warning(f"Evaluation {evaluation_id} not found")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting evaluation {evaluation_id}: {str(e)}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            return False
    
    def export_evaluations_csv(self, output_path: str) -> bool:
        """Export evaluations to CSV"""
        try:
            import csv
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT id, team_name, problem_statement, file_name, 
                       final_score, normalized_score, percentage_score, grade, 
                       timestamp, created_at
                FROM evaluations
                ORDER BY percentage_score DESC
                ''')
                
                rows = cursor.fetchall()
                
                with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    writer.writerow([
                        'ID', 'Team Name', 'Problem Statement', 'File Name',
                        'Final Score', 'Normalized Score', 'Percentage Score', 'Grade',
                        'Timestamp', 'Created At'
                    ])
                    
                    # Data
                    writer.writerows(rows)
                
                logger.info(f"Evaluations exported to {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error exporting evaluations: {str(e)}")
            return False
    
    def get_component_analysis(self) -> Dict[str, Any]:
        """Get detailed component analysis across all evaluations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                analysis = {}
                
                # Component score statistics
                cursor.execute('''
                SELECT component_name, 
                       COUNT(*) as count,
                       AVG(raw_score) as avg_score,
                       MIN(raw_score) as min_score,
                       MAX(raw_score) as max_score,
                       AVG(weighted_score) as avg_weighted
                FROM component_scores
                GROUP BY component_name
                ''')
                
                components = cursor.fetchall()
                
                for comp_name, count, avg, min_score, max_score, avg_weighted in components:
                    analysis[comp_name] = {
                        'count': count,
                        'average_raw_score': round(avg, 3),
                        'min_score': round(min_score, 3),
                        'max_score': round(max_score, 3),
                        'average_weighted_score': round(avg_weighted, 3),
                        'score_range': round(max_score - min_score, 3)
                    }
                
                return analysis
                
        except Exception as e:
            logger.error(f"Error getting component analysis: {str(e)}")
            return {}