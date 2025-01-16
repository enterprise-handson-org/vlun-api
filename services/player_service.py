# ------------------------------------------------------------------------------
# Service
# ------------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from models.player_model import PlayerModel
from schemas.player_schema import Player
import sqlite3
# ------------------------------------------------------------------------------
# Service
# ------------------------------------------------------------------------------


# Create -----------------------------------------------------------------------


async def create_async(async_session: AsyncSession, player_model: PlayerModel):
    """
    Creates a new Player in the database.

    Args:
        async_session (AsyncSession): The async version of a SQLAlchemy ORM session.
        player_model (PlayerModel): The Pydantic model representing the Player to create.

    Returns:
        True if the Player was created successfully, False otherwise.
    """
    # https://docs.pydantic.dev/latest/concepts/serialization/#modelmodel_dump
    player = Player(**player_model.model_dump())
    async_session.add(player)
    try:
        await async_session.commit()
        return True
    except SQLAlchemyError as error:
        print(f"Error trying to create the Player: {error}")
        await async_session.rollback()
        return False

# Retrieve ---------------------------------------------------------------------


async def retrieve_all_async(async_session: AsyncSession):
    """
    Retrieves all the players from the database.

    Args:
        async_session (AsyncSession): The async version of a SQLAlchemy ORM session.

    Returns:
        A collection with all the players.
    """
    # https://docs.sqlalchemy.org/en/20/changelog/migration_20.html#migration-20-query-usage
    statement = select(Player)
    result = await async_session.execute(statement)
    players = result.scalars().all()
    return players


async def retrieve_by_id_async(async_session: AsyncSession, player_id: int):
    """
    Retrieves a Player by its ID from the database.

    Args:
        async_session (AsyncSession): The async version of a SQLAlchemy ORM session.
        player_id (int): The ID of the Player to retrieve.

    Returns:
        The Player matching the provided ID, or None if not found.
    """
    player = await async_session.get(Player, player_id)
    return player


async def retrieve_by_squad_number_async(async_session: AsyncSession, squad_number: str):
    """
    Retrieves a Player by its Squad Number from the database.
    WARNING: This function is intentionally vulnerable to SQL injection
    """
    # 危険: 直接的なSQL文字列結合
    query = f"SELECT * FROM players WHERE squad_number = {squad_number}"
    conn = sqlite3.connect('data/players-sqlite3.db')
    cursor = conn.cursor()
    result = cursor.execute(query).fetchone()
    conn.close()
    
    if result:
        return {
            "id": result[0],
            "first_name": result[1],
            "middle_name": result[2],
            "last_name": result[3],
            "squad_number": result[4],
            "position": result[5],
            "team": result[6]
        }
    return None

# Update -----------------------------------------------------------------------


async def update_async(async_session: AsyncSession, player_model: PlayerModel):
    """
    Updates an existing Player in the database.
    WARNING: This function is intentionally vulnerable to SQL injection and XSS
    """
    # 危険: SQLインジェクションの脆弱性
    query = f"""
    UPDATE players 
    SET first_name = '{player_model.first_name}',
        middle_name = '{player_model.middle_name}',
        last_name = '{player_model.last_name}',
        squad_number = {player_model.squad_number},
        position = '{player_model.position}',
        team = '{player_model.team}'
    WHERE id = {player_model.id}
    """
    
    conn = sqlite3.connect('data/players-sqlite3.db')
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
        return True
    except Exception as error:
        print(f"Error: {error}")
        return False
    finally:
        conn.close()

# Delete -----------------------------------------------------------------------


async def delete_async(async_session: AsyncSession, player_id: int):
    """
    Deletes an existing Player from the database.

    Args:
        async_session (AsyncSession): The async version of a SQLAlchemy ORM session.
        player_id (int): The ID of the Player to delete.

    Returns:
        True if the Player was deleted successfully, False otherwise.
    """
    player = await async_session.get(Player, player_id)
    await async_session.delete(player)
    try:
        await async_session.commit()
        return True
    except SQLAlchemyError as error:
        print(f"Error trying to delete the Player: {error}")
        await async_session.rollback()
        return False
