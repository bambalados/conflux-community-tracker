"""
Database module for storing and retrieving member count data
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class MemberCount(Base):
    """Table for storing member counts"""
    __tablename__ = 'member_counts'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    group_name = Column(String(50), nullable=False, index=True)
    member_count = Column(Integer, nullable=False)

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_group_timestamp', 'group_name', 'timestamp'),
    )

    def __repr__(self):
        return f"<MemberCount(group={self.group_name}, count={self.member_count}, time={self.timestamp})>"


class MemberDatabase:
    """Database manager for member counts"""

    def __init__(self, db_path: str = "data/members.db"):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Create engine and session
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_member_counts(self, counts: Dict[str, int], timestamp: Optional[datetime] = None):
        """
        Add member counts for multiple groups

        Args:
            counts: Dictionary mapping group names to member counts
            timestamp: Timestamp for the data (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        for group_name, count in counts.items():
            if count is not None:  # Skip failed scrapes
                record = MemberCount(
                    timestamp=timestamp,
                    group_name=group_name,
                    member_count=count
                )
                self.session.add(record)

        self.session.commit()

    def get_all_data(self) -> pd.DataFrame:
        """
        Get all member count data

        Returns:
            DataFrame with columns: timestamp, group_name, member_count
        """
        query = self.session.query(MemberCount).order_by(MemberCount.timestamp)
        return pd.read_sql(query.statement, self.engine)

    def get_group_data(self, group_name: str) -> pd.DataFrame:
        """
        Get data for a specific group

        Args:
            group_name: Name of the group

        Returns:
            DataFrame with columns: timestamp, member_count
        """
        query = self.session.query(
            MemberCount.timestamp,
            MemberCount.member_count
        ).filter(
            MemberCount.group_name == group_name
        ).order_by(MemberCount.timestamp)

        df = pd.read_sql(query.statement, self.engine)
        return df

    def get_latest_counts(self) -> Dict[str, Tuple[int, datetime]]:
        """
        Get the most recent member count for each group

        Returns:
            Dictionary mapping group names to (count, timestamp) tuples
        """
        # Get latest timestamp
        latest_query = self.session.query(MemberCount.timestamp).order_by(
            MemberCount.timestamp.desc()
        ).limit(1)

        latest_time = latest_query.first()
        if not latest_time:
            return {}

        latest_time = latest_time[0]

        # Get all counts from that timestamp
        query = self.session.query(MemberCount).filter(
            MemberCount.timestamp == latest_time
        )

        results = {}
        for record in query:
            results[record.group_name] = (record.member_count, record.timestamp)

        return results

    def get_previous_counts(self, before_timestamp: datetime) -> Dict[str, int]:
        """
        Get member counts from the collection period before the given timestamp

        Args:
            before_timestamp: Get counts before this time

        Returns:
            Dictionary mapping group names to member counts
        """
        # Get the most recent timestamp before the given one
        prev_query = self.session.query(MemberCount.timestamp).filter(
            MemberCount.timestamp < before_timestamp
        ).order_by(MemberCount.timestamp.desc()).limit(1)

        prev_time = prev_query.first()
        if not prev_time:
            return {}

        prev_time = prev_time[0]

        # Get all counts from that timestamp
        query = self.session.query(MemberCount).filter(
            MemberCount.timestamp == prev_time
        )

        results = {}
        for record in query:
            results[record.group_name] = record.member_count

        return results

    def get_aggregated_totals(self) -> pd.DataFrame:
        """
        Get aggregated total member counts over time

        Returns:
            DataFrame with columns: timestamp, total_members
        """
        query = """
        SELECT timestamp, SUM(member_count) as total_members
        FROM member_counts
        GROUP BY timestamp
        ORDER BY timestamp
        """
        df = pd.read_sql(query, self.engine)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def get_all_groups(self) -> List[str]:
        """
        Get list of all group names in database

        Returns:
            List of group names
        """
        query = self.session.query(MemberCount.group_name).distinct()
        return [row[0] for row in query]

    def clear_all_data(self):
        """Clear all data from database (use with caution!)"""
        self.session.query(MemberCount).delete()
        self.session.commit()

    def close(self):
        """Close database connection"""
        self.session.close()


if __name__ == "__main__":
    # Test the database
    db = MemberDatabase()

    # Add some test data
    test_counts = {
        "English": 5000,
        "Africa": 2800,
        "Korea": 700,
    }

    db.add_member_counts(test_counts)
    print("Added test data")

    # Retrieve data
    print("\nAll data:")
    print(db.get_all_data())

    print("\nLatest counts:")
    print(db.get_latest_counts())

    print("\nAggregated totals:")
    print(db.get_aggregated_totals())

    db.close()
