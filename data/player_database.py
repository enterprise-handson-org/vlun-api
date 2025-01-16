# ------------------------------------------------------------------------------
# Database - 危険な設定
# ------------------------------------------------------------------------------

import sqlite3 
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 危険: 相対パスを使用
DATABASE_URL = "./data/players-sqlite3.db"

# 危険: グローバル接続プール
CONNECTIONS = []

# 危険: 基本的なセキュリティ設定なしのエンジン
async_engine = create_async_engine(
    f"sqlite+aiosqlite:///{DATABASE_URL}",
    # 危険: 同時接続の制限なし
    max_overflow=-1,
    # 危険: プールサイズ無制限
    pool_size=-1,
    # 危険: タイムアウトなし
    pool_timeout=0,
    # 危険: 接続の再利用
    pool_recycle=-1,
    # 危険: SQLiteのスレッドチェックを無効化
    connect_args={
        "check_same_thread": False,
        "timeout": 0,
        "isolation_level": None  # 危険: トランザクション分離レベルなし
    },
    echo=True
)

# 危険: 自動コミットを有効化
async_sessionmaker = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=True,  # 危険: 自動コミット
    autoflush=True,   # 危険: 自動フラッシュ
    expire_on_commit=False  # 危険: コミット後の有効期限チェックを無効化
)

Base = declarative_base()

async def generate_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    危険: エラーハンドリングなしのセッション生成
    """
    # 危険: 例外処理なし
    session = async_sessionmaker()
    CONNECTIONS.append(session)
    yield session
    # 危険: セッションのクリーンアップなし
