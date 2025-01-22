from .session import SESSION as S
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Bot:
    bot_id: int
    name: str
    tagline: Optional[str]
    description: str
    image_url: Optional[str]
    type: str
    source: str
    created_at: datetime

    def __getitem__(self, key):
        return {
            'BOT_ID': self.bot_id,
            'NAME': self.name,
            'TAGLINE': self.tagline,
            'DESCRIPTION': self.description,
            'IMAGE_URL': self.image_url,
            'TYPE': self.type,
            'SOURCE': self.source,
            'CREATED_AT': self.created_at
        }[key.upper()]

    def to_dict(self):
        return {
            'BOT_ID': self.bot_id,
            'NAME': self.name,
            'TAGLINE': self.tagline,
            'DESCRIPTION': self.description,
            'IMAGE_URL': self.image_url,
            'TYPE': self.type,
            'SOURCE': self.source,
            'CREATED_AT': self.created_at
        }


def create_bot(name: str, tagline: str, description: str, image_url: str, type: str, source: str) -> Bot:
    """Create a bot with auto-generated ID"""
    S.sql("""
        INSERT INTO BOTS (NAME, TAGLINE, DESCRIPTION, IMAGE_URL, TYPE, SOURCE) 
        VALUES (?, ?, ?, ?, ?)
    """, params=[name, tagline, description, image_url, type, source]).collect()
    S.sql("COMMIT").collect()
    bot = S.sql(
        "SELECT * FROM BOTS ORDER BY CREATED_AT DESC").collect()[0]
    print("Bot created successfully")
    return bot['BOT_ID']


def get_bots() -> List[Bot]:
    """Get all bots"""
    results = S.sql("SELECT * FROM BOTS ORDER BY CREATED_AT DESC").collect()
    return [Bot(
        bot_id=row['BOT_ID'],
        name=row['NAME'],
        tagline=row['TAGLINE'],
        description=row['DESCRIPTION'],
        image_url=row['IMAGE_URL'],
        type=row['TYPE'],
        source=row['SOURCE'],
        created_at=row['CREATED_AT']
    ) for row in results]


def get_bot(bot_id: int) -> Optional[Bot]:
    """Get a bot by ID"""
    result = S.sql("SELECT * FROM BOTS WHERE BOT_ID = ?",
                   params=[bot_id]).collect()
    if not result:
        return None

    bot_data = result[0]

    return Bot(
        bot_id=bot_data['BOT_ID'],
        name=bot_data['NAME'],
        tagline=bot_data['TAGLINE'],
        description=bot_data['DESCRIPTION'],
        image_url=bot_data['IMAGE_URL'],
        type=bot_data['TYPE'],
        source=bot_data['SOURCE'],
        created_at=bot_data['CREATED_AT']
    )
