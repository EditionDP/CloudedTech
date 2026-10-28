from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DiscordEducationalResponse(Base):
    __tablename__ = "discord_educational_responses"

    __table_args__ = (
        UniqueConstraint("clave_unica", name="uq_discord_educational_clave"),
        UniqueConstraint(
            "guild_id",
            "channel_id",
            "source_message_id",
            name="uq_discord_educational_origen",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    clave_unica: Mapped[str] = mapped_column(String(64), nullable=False)

    guild_id: Mapped[str] = mapped_column(String(32), nullable=False)
    channel_id: Mapped[str] = mapped_column(String(32), nullable=False)
    source_message_id: Mapped[str] = mapped_column(String(32), nullable=False)

    pregunta_original: Mapped[str] = mapped_column(Text, nullable=False)
    respuesta: Mapped[str | None] = mapped_column(Text, nullable=True)

    tema: Mapped[str | None] = mapped_column(String(100), nullable=True)

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="borrador",
    )

    discord_message_id: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )

    error_detalle: Mapped[str | None] = mapped_column(Text, nullable=True)

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    publicado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
