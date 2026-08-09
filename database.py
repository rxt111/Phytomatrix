import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///phytomatrix_rnd.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Botanical(Base):
    __tablename__ = "botanicals"
    id = Column(Integer, primary_key=True, index=True)
    latin_name = Column(String(255), unique=True, nullable=False)
    common_name = Column(String(255), nullable=False)
    family = Column(String(255), nullable=False)
    synonyms_json = Column(Text, default="[]")
    genus_species_json = Column(Text, default="[]")
    traditional_json = Column(Text, default="{}")
    phytochemicals = relationship("Phytochemical", back_populates="botanical", cascade="all, delete-orphan")

class Phytochemical(Base):
    __tablename__ = "phytochemicals"
    id = Column(Integer, primary_key=True, index=True)
    botanical_id = Column(Integer, ForeignKey("botanicals.id"), nullable=False)
    name = Column(String(255), nullable=False)
    chemical_class = Column(String(255), nullable=False)
    plant_part = Column(String(255), nullable=False)
    status = Column(String(255), default="Bioactive")
    mw = Column(Float, default=0.0)
    logp = Column(Float, default=0.0)
    tpsa = Column(Float, default=0.0)
    lipinski = Column(String(100), default="Pass")
    botanical = relationship("Botanical", back_populates="phytochemicals")

class Formulation(Base):
    __tablename__ = "formulations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    target_fill_mg = Column(Float, default=500.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    items = relationship("FormulationItem", back_populates="formulation", cascade="all, delete-orphan")

class FormulationItem(Base):
    __tablename__ = "formulation_items"
    id = Column(Integer, primary_key=True, index=True)
    formulation_id = Column(Integer, ForeignKey("formulations.id"), nullable=False)
    botanical_latin_name = Column(String(255), nullable=False)
    plant_part = Column(String(255), nullable=False)
    extract_grade = Column(String(255), nullable=False)
    unit_mass_mg = Column(Float, nullable=False)
    formulation = relationship("Formulation", back_populates="items")

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Safe SQLite in-place schema migration
    inspector = inspect(engine)
    if inspector.has_table("botanicals"):
        columns = [c["name"] for c in inspector.get_columns("botanicals")]
        if "traditional_json" not in columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE botanicals ADD COLUMN traditional_json TEXT DEFAULT '{}'"))
                conn.commit()

    session = SessionLocal()
    try:
        if session.query(Botanical).count() == 0:
            from seed_data import BOTANICAL_SEED_LIBRARY
            for b_data in BOTANICAL_SEED_LIBRARY:
                bot = Botanical(
                    latin_name=b_data["latin_name"],
                    common_name=b_data["common_name"],
                    family=b_data["family"],
                    synonyms_json=json.dumps(b_data["synonyms"]),
                    genus_species_json=json.dumps(b_data["genus_species"]),
                    traditional_json=json.dumps(b_data.get("traditional_data", {}))
                )
                session.add(bot)
                session.commit()
                for p_data in b_data["phytochemicals"]:
                    session.add(Phytochemical(
                        botanical_id=bot.id,
                        name=p_data["name"],
                        chemical_class=p_data["class"],
                        plant_part=p_data["part"],
                        status=p_data["status"],
                        mw=p_data["mw"],
                        logp=p_data["logp"],
                        tpsa=p_data["tpsa"],
                        lipinski=p_data["lipinski"]
                    ))
                session.commit()
        else:
            # Backfill traditional_json for existing records if missing
            from seed_data import BOTANICAL_SEED_LIBRARY
            for b_data in BOTANICAL_SEED_LIBRARY:
                bot = session.query(Botanical).filter_by(latin_name=b_data["latin_name"]).first()
                if bot and (not bot.traditional_json or bot.traditional_json == "{}"):
                    bot.traditional_json = json.dumps(b_data.get("traditional_data", {}))
            session.commit()
    finally:
        session.close()

def get_saved_formulations() -> list:
    session = SessionLocal()
    try:
        forms = session.query(Formulation).order_by(Formulation.created_at.desc()).all()
        return [{
            "id": f.id,
            "name": f.name,
            "target_fill_mg": f.target_fill_mg,
            "created_at": f.created_at.strftime("%Y-%m-%d %H:%M"),
            "items": [{"latin_name": i.botanical_latin_name, "part": i.plant_part, "standardization": i.extract_grade, "unit_mass_mg": i.unit_mass_mg} for i in f.items]
        } for f in forms]
    finally:
        session.close()
