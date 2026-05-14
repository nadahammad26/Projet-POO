from flask_sqlalchemy import SQLAlchemy
from typing import List

# On initialise l'objet db, qui sera lié à notre application Flask dans app.py
db = SQLAlchemy()

# ============================================================
# TABLES D'ASSOCIATION (Relations Many-to-Many)
# ============================================================

# Table pour lier les Membres et les Clubs (qui est membre de quel club)
club_membres = db.Table('club_membres',
    db.Column('membre_id', db.Integer, db.ForeignKey('membre.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

# Table pour lier les Membres et les Événements (qui participe à quel événement)
event_membres = db.Table('event_membres',
    db.Column('membre_id', db.Integer, db.ForeignKey('membre.id'), primary_key=True),
    db.Column('evenement_id', db.Integer, db.ForeignKey('evenement.id'), primary_key=True)
)

# ============================================================
# CLASSE MEMBRE (ET PRESIDENT via Héritage)
# ============================================================

class Membre(db.Model):
    __tablename__ = 'membre'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Colonne pour l'héritage polymorphique
    type_membre = db.Column(db.String(50))
    
    # [LIMITE/ENCAPSULATION] Attributs protégés avec mapping vers colonnes SQL
    _nom = db.Column('nom', db.String(100), nullable=False)
    _prenom = db.Column('prenom', db.String(100), nullable=False)
    _email = db.Column('email', db.String(120), unique=True, nullable=False)
    _password = db.Column('password', db.String(100), nullable=False)
    filiere = db.Column(db.String(100))
    telephone = db.Column(db.String(20))
    
    # Relations
    clubs_rejoints = db.relationship('Club', secondary=club_membres, backref=db.backref('membres', lazy=True))
    evenements_inscrits = db.relationship('Evenement', secondary=event_membres, backref=db.backref('membres_inscrits', lazy=True))

    __mapper_args__ = {
        'polymorphic_identity': 'membre',
        'polymorphic_on': type_membre
    }

    # [GETTERS / SETTERS] Pour l'encapsulation
    @property
    def nom(self):
        return self._nom

    @nom.setter
    def nom(self, value):
        if not value or len(value) < 2:
            raise ValueError("Nom invalide")
        self._nom = value
    
    nom = db.synonym('_nom', descriptor=nom)

    @property
    def prenom(self):
        return self._prenom

    @prenom.setter
    def prenom(self, value):
        if not value:
            raise ValueError("Prénom invalide")
        self._prenom = value
    
    prenom = db.synonym('_prenom', descriptor=prenom)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if "@" not in value:
            raise ValueError("Email invalide")
        self._email = value
    
    email = db.synonym('_email', descriptor=email)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if len(value) < 4:
            raise ValueError("Mot de passe trop court")
        self._password = value
    
    password = db.synonym('_password', descriptor=password)

    # [FORME/POLYMORPHISME] Méthode à redéfinir
    def obtenir_role(self):
        return "Membre standard"

    def rejoindre_club(self, club: "Club"):
        if club not in self.clubs_rejoints:
            self.clubs_rejoints.append(club)

class President(Membre):
    __mapper_args__ = {
        'polymorphic_identity': 'president'
    }
    
    # Relation One-to-Many
    clubs_geres = db.relationship('Club', backref='president', lazy=True)

    # [FORME/POLYMORPHISME] Redéfinition de la méthode
    def obtenir_role(self):
        return "Président de club"

    def ajouter_evenement(self, club: "Club", evenement: "Evenement"):
        # [COMPOSITION] Le président délègue au club la gestion de ses événements
        if club.president == self:
            club.ajouter_evenement_direct(evenement)

    def supprimer_membre(self, club: "Club", membre: Membre):
        if club.president == self and membre in club.membres:
            club.membres.remove(membre)

# ============================================================
# CLASSE CLUB
# ============================================================

class Club(db.Model):
    __tablename__ = 'club'
    
    id = db.Column(db.Integer, primary_key=True)
    _nom = db.Column('nom', db.String(100), nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(50))
    date_creation = db.Column(db.String(20))
    
    president_id = db.Column(db.Integer, db.ForeignKey('membre.id'))
    
    # Un club a plusieurs événements
    evenements = db.relationship('Evenement', backref='club', cascade="all, delete-orphan", lazy=True)

    @property
    def nom(self):
        return self._nom

    @nom.setter
    def nom(self, value):
        self._nom = value
    
    nom = db.synonym('_nom', descriptor=nom)

    # [COMPOSITION] Gestion interne des événements
    def ajouter_evenement_direct(self, evenement: "Evenement"):
        self.evenements.append(evenement)

# ============================================================
# CLASSE EVENEMENT
# ============================================================

class Evenement(db.Model):
    __tablename__ = 'evenement'
    
    id = db.Column(db.Integer, primary_key=True)
    _titre = db.Column('titre', db.String(100), nullable=False)
    date = db.Column(db.String(20))
    description = db.Column(db.Text)
    adhesion = db.Column(db.String(20))  # Gratuit / Payant
    termine = db.Column(db.Boolean, default=False)
    
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    
    @property
    def titre(self):
        return self._titre

    @titre.setter
    def titre(self, value):
        self._titre = value
    
    titre = db.synonym('_titre', descriptor=titre)

    def statut(self):
        return "Terminé" if self.termine else "En cours"
