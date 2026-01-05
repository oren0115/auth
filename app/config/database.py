"""Manajemen koneksi database menggunakan Prisma Client."""
from prisma import Prisma
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

# Instance global Prisma client (singleton pattern)
prisma_client: Prisma | None = None


async def connect_db() -> None:
    """Membuka koneksi ke database (dipanggil saat startup)."""
    global prisma_client
    if prisma_client is None:
        prisma_client = Prisma()
        await prisma_client.connect()
        logger.info("Database connected")


async def disconnect_db() -> None:
    """Menutup koneksi database (dipanggil saat shutdown)."""
    global prisma_client
    if prisma_client is not None:
        await prisma_client.disconnect()
        prisma_client = None
        logger.info("Database disconnected")


@asynccontextmanager
async def get_db() -> AsyncGenerator[Prisma, None]:
    """Dependency injection untuk mendapatkan Prisma client di FastAPI routes."""
    global prisma_client
    if prisma_client is None:
        await connect_db()
    try:
        yield prisma_client
    finally:
        pass  # Lifecycle dikelola oleh lifespan di main.py


def get_prisma() -> Prisma:
    """Mendapatkan instance Prisma client yang sudah terhubung."""
    global prisma_client
    if prisma_client is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return prisma_client

