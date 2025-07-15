"""
Git-related test data factories.

This module provides factories for creating realistic git objects like
commits, branches, and repository states.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .base import BaseFactory, Faker, generate_commit_message, SequenceMixin


class GitCommitFactory(BaseFactory, SequenceMixin):
    """Factory for creating realistic git commit objects."""
    
    @staticmethod
    def hash() -> str:
        """Generate a realistic git commit hash."""
        return Faker.hex_string(40)
    
    @staticmethod
    def short_hash() -> str:
        """Generate a short git commit hash."""
        return Faker.hex_string(8)
    
    @staticmethod
    def message() -> str:
        """Generate a realistic commit message."""
        return generate_commit_message()
    
    @staticmethod
    def author_name() -> str:
        """Generate author name."""
        return Faker.name()
    
    @staticmethod
    def author_email() -> str:
        """Generate author email."""
        return Faker.email()
    
    @staticmethod
    def timestamp() -> datetime:
        """Generate commit timestamp."""
        return Faker.date_time()
    
    @staticmethod
    def files_changed() -> int:
        """Generate number of files changed."""
        return Faker.random_int(1, 8)
    
    @staticmethod
    def lines_added() -> int:
        """Generate lines added."""
        return Faker.random_int(1, 150)
    
    @staticmethod
    def lines_removed() -> int:
        """Generate lines removed."""
        return Faker.random_int(0, 75)
    
    # Trait methods for different commit types
    @classmethod
    def trait_feature(cls) -> Dict[str, Any]:
        """Trait for feature commits."""
        return {
            'message': generate_commit_message('feat'),
            'lines_added': Faker.random_int(20, 200),
            'files_changed': Faker.random_int(2, 8)
        }
    
    @classmethod
    def trait_bugfix(cls) -> Dict[str, Any]:
        """Trait for bugfix commits."""
        return {
            'message': generate_commit_message('fix'),
            'lines_added': Faker.random_int(5, 50),
            'lines_removed': Faker.random_int(1, 20),
            'files_changed': Faker.random_int(1, 3)
        }
    
    @classmethod
    def trait_docs(cls) -> Dict[str, Any]:
        """Trait for documentation commits."""
        return {
            'message': generate_commit_message('docs'),
            'lines_added': Faker.random_int(5, 100),
            'files_changed': Faker.random_int(1, 3)
        }
    
    @classmethod
    def trait_large(cls) -> Dict[str, Any]:
        """Trait for large commits."""
        return {
            'lines_added': Faker.random_int(200, 1000),
            'lines_removed': Faker.random_int(50, 300),
            'files_changed': Faker.random_int(10, 25)
        }
    
    @classmethod
    def trait_small(cls) -> Dict[str, Any]:
        """Trait for small commits."""
        return {
            'lines_added': Faker.random_int(1, 20),
            'lines_removed': Faker.random_int(0, 10),
            'files_changed': Faker.random_int(1, 3)
        }


class GitBranchFactory(BaseFactory):
    """Factory for creating git branch objects."""
    
    @staticmethod
    def name() -> str:
        """Generate a realistic branch name."""
        branch_types = ['feature', 'bugfix', 'hotfix', 'release', 'develop']
        descriptors = [
            'auth', 'api', 'ui', 'database', 'performance', 'security',
            'user-management', 'data-processing', 'error-handling'
        ]
        
        branch_type = random.choice(branch_types)
        descriptor = random.choice(descriptors)
        number = random.randint(1, 999)
        
        if branch_type in ['develop', 'main', 'master']:
            return branch_type
        elif branch_type == 'release':
            major = random.randint(1, 3)
            minor = random.randint(0, 9)
            patch = random.randint(0, 9)
            return f"{branch_type}/v{major}.{minor}.{patch}"
        else:
            return f"{branch_type}/{descriptor}-{number}"
    
    @staticmethod
    def commit_hash() -> str:
        """Generate commit hash for branch HEAD."""
        return GitCommitFactory.hash()
    
    @staticmethod
    def is_remote() -> bool:
        """Whether branch exists on remote."""
        return Faker.weighted_choice([True, False], [0.7, 0.3])
    
    @staticmethod
    def ahead_by() -> int:
        """Commits ahead of main/develop."""
        return Faker.random_int(0, 10)
    
    @staticmethod
    def behind_by() -> int:
        """Commits behind main/develop."""
        return Faker.random_int(0, 5)
    
    @staticmethod
    def last_commit_date() -> datetime:
        """Last commit date on this branch."""
        return Faker.date_time()
    
    # Trait methods
    @classmethod
    def trait_main_branch(cls) -> Dict[str, Any]:
        """Trait for main/master branches."""
        return {
            'name': random.choice(['main', 'master']),
            'behind_by': 0,
            'is_remote': True
        }
    
    @classmethod
    def trait_feature_branch(cls) -> Dict[str, Any]:
        """Trait for feature branches."""
        features = ['auth', 'api', 'ui', 'dashboard', 'reporting', 'integration']
        feature = random.choice(features)
        return {
            'name': f"feature/{feature}-{random.randint(100, 999)}",
            'ahead_by': Faker.random_int(1, 15),
            'behind_by': Faker.random_int(0, 3)
        }
    
    @classmethod
    def trait_stale_branch(cls) -> Dict[str, Any]:
        """Trait for stale/old branches."""
        return {
            'last_commit_date': datetime.now() - timedelta(days=random.randint(30, 180)),
            'behind_by': Faker.random_int(10, 50)
        }


class GitRepositoryStateFactory(BaseFactory):
    """Factory for creating complete git repository state."""
    
    @staticmethod
    def current_branch() -> str:
        """Current active branch."""
        return GitBranchFactory.name()
    
    @staticmethod
    def default_branch() -> str:
        """Default repository branch."""
        return random.choice(['main', 'master', 'develop'])
    
    @staticmethod
    def is_dirty() -> bool:
        """Whether repository has uncommitted changes."""
        return Faker.weighted_choice([True, False], [0.6, 0.4])
    
    @staticmethod
    def total_commits() -> int:
        """Total commits in repository."""
        return Faker.random_int(10, 1000)
    
    @staticmethod
    def total_branches() -> int:
        """Total number of branches."""
        return Faker.random_int(1, 10)
    
    @staticmethod
    def stash_count() -> int:
        """Number of stash entries."""
        return Faker.random_int(0, 5)
    
    @staticmethod
    def ahead_by() -> int:
        """Commits ahead of remote."""
        return Faker.random_int(0, 10)
    
    @staticmethod
    def behind_by() -> int:
        """Commits behind remote."""
        return Faker.random_int(0, 5)
    
    @staticmethod
    def remote_url() -> str:
        """Repository remote URL."""
        return Faker.url()
    
    @staticmethod
    def last_commit_hash() -> str:
        """Last commit hash."""
        return GitCommitFactory.hash()
    
    @staticmethod
    def last_commit_message() -> str:
        """Last commit message."""
        return GitCommitFactory.message()
    
    @staticmethod
    def last_commit_date() -> datetime:
        """Last commit date."""
        return Faker.date_time()
    
    @classmethod
    def create(cls, **kwargs) -> Dict[str, Any]:
        """Create repository state with related objects."""
        state = super().create(**kwargs)
        
        # Generate related collections
        state['branches'] = [
            GitBranchFactory.create() for _ in range(state['total_branches'])
        ]
        
        # Generate recent commits
        commit_count = min(state['total_commits'], 20)
        state['recent_commits'] = [
            GitCommitFactory.create() for _ in range(commit_count)
        ]
        
        # Generate stash entries
        state['stash_entries'] = []
        for i in range(state['stash_count']):
            state['stash_entries'].append({
                'index': i,
                'message': f"WIP: {Faker.sentence(nb_words=4)}",
                'timestamp': Faker.date_time(),
                'files_count': Faker.random_int(1, 8)
            })
        
        return state
    
    # Trait methods
    @classmethod
    def trait_clean(cls) -> Dict[str, Any]:
        """Trait for clean repository (no uncommitted changes)."""
        return {
            'is_dirty': False,
            'ahead_by': 0,
            'behind_by': 0,
            'stash_count': 0
        }
    
    @classmethod
    def trait_dirty(cls) -> Dict[str, Any]:
        """Trait for dirty repository (many changes)."""
        return {
            'is_dirty': True,
            'ahead_by': Faker.random_int(3, 10),
            'stash_count': Faker.random_int(1, 5)
        }
    
    @classmethod
    def trait_large(cls) -> Dict[str, Any]:
        """Trait for large repository."""
        return {
            'total_commits': Faker.random_int(500, 5000),
            'total_branches': Faker.random_int(10, 50)
        }


class GitDiffFactory(BaseFactory):
    """Factory for creating git diff information."""
    
    @staticmethod
    def file_path() -> str:
        """File path for diff."""
        return Faker.file_path()
    
    @staticmethod
    def lines_added() -> int:
        """Lines added in diff."""
        return Faker.random_int(0, 100)
    
    @staticmethod
    def lines_removed() -> int:
        """Lines removed in diff."""
        return Faker.random_int(0, 50)
    
    @staticmethod
    def change_type() -> str:
        """Type of change."""
        return Faker.random_element(['modified', 'added', 'deleted', 'renamed'])
    
    @staticmethod
    def similarity() -> float:
        """Similarity percentage for renames."""
        return Faker.pyfloat(0.0, 1.0)
    
    @staticmethod
    def is_binary() -> bool:
        """Whether file is binary."""
        return Faker.weighted_choice([False, True], [0.8, 0.2])
    
    @staticmethod
    def hunks() -> List[Dict[str, Any]]:
        """Generate diff hunks."""
        hunk_count = Faker.random_int(1, 5)
        hunks = []
        
        for i in range(hunk_count):
            hunks