from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    complete_name = Column(String(100))
    company_name = Column(String(100))
    company_address = Column(Text)
    company_email = Column(String(100))
    company_phone = Column(String(20))
    company_logo = Column(String(255))
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BillingRecord(Base):
    __tablename__ = 'billing_records'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(Text)
    billing_date = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='billing_records')

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)

    user = relationship('User', back_populates='subscriptions')

User.billing_records = relationship('BillingRecord', order_by=BillingRecord.id, back_populates='user')
User.subscriptions = relationship('Subscription', order_by=Subscription.id, back_populates='user')

class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    generated_at = Column(DateTime, nullable=False)
    file_path = Column(Text, nullable=False)

    user = relationship('User', back_populates='reports')

User.reports = relationship('Report', order_by=Report.id, back_populates='user')

class Analytics(Base):
    __tablename__ = 'analytics'

    id = Column(Integer, primary_key=True)
    data_json = Column(Text, nullable=False)

class FrontendSettings(Base):
    __tablename__ = 'frontend_settings'

    id = Column(Integer, primary_key=True)
    settings_json = Column(Text, nullable=False)

# Database setup
engine = create_engine('sqlite:///terminusa.db', echo=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
