from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'users'

    is_guest: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    provider_sub: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    allow_sync: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_analytics: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    checkins = relationship('MoodCheckIn', back_populates='user', cascade='all, delete-orphan')
    journal_entries = relationship('JournalEntry', back_populates='user', cascade='all, delete-orphan')
    pomodoro_sessions = relationship('PomodoroSession', back_populates='user', cascade='all, delete-orphan')
    crisis_events = relationship('CrisisEvent', back_populates='user', cascade='all, delete-orphan')


class MoodCheckIn(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'mood_checkins'

    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    mood_score: Mapped[int] = mapped_column(Integer, nullable=False)
    stress_score: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship('User', back_populates='checkins')


class JournalEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'journal_entries'

    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user = relationship('User', back_populates='journal_entries')


class Exercise(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'exercises'

    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    steps: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PomodoroSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'pomodoro_sessions'

    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    focus_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    break_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    cycles_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship('User', back_populates='pomodoro_sessions')


class CrisisEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'crisis_events'

    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    trigger_text: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default='high')

    user = relationship('User', back_populates='crisis_events')
