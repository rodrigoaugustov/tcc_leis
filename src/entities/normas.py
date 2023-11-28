from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Text

Base = declarative_base()


class Normas(Base):
    __tablename__ = 'normas'
    id = Column(Integer, primary_key=True)
    titulo = Column(Text)
    nr_norma = Column(Integer)
    ementa = Column(Text)
    data_norma = Column(DateTime)
    data_captura = Column(DateTime)
    url = Column(Text)
    indexacao = Column(Text)
    texto = Column(Text(64000))

    def __repr__(self):
        return f"<Normas(\
            titulo='{self.titulo}', \
            nr_norma={self.nr_norma}, \
            ementa='{self.ementa}', \
            url='{self.url}', \
            data_norma={self.data_norma}, \
            data_captura={self.data_captura}, \
            indexacao='{self.indexacao}', \
            texto='{self.texto}'\
            )>"