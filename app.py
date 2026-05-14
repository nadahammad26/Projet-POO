import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Membre, President, Club, Evenement

app = Flask(__name__)
app.secret_key = "super_secret_key_pour_les_sessions"

# Configuration de la base de données SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'clubconnect.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base de données avec l'application Flask
db.init_app(app)

# ============================================================
# INITIALISATION DES DONNÉES DE DÉMONSTRATION (Si DB vide)
# ============================================================
def init_db():
    with app.app_context():
        db.create_all()
        
        if not President.query.first():
            print("Initialisation avec les nouveaux clubs...")
            
            # Création des présidents
            pres1 = President(nom="Zidane", prenom="Abdel", email="abdel.zidane@email.com", password="pass123", filiere="Génie Logiciel", telephone="0601020304")
            pres2 = President(nom="Lalami", prenom="Sara", email="sara.lalami@email.com", password="pass456", filiere="Management", telephone="0605060708")
            pres3 = President(nom="El Amrani", prenom="Yassine", email="yassine.elamrani@email.com", password="pass789", filiere="Design", telephone="0609101112")
            pres4 = President(nom="Bennani", prenom="Sofia", email="sofia.bennani@email.com", password="pass321", filiere="Social", telephone="0613141516")
            
            db.session.add_all([pres1, pres2, pres3, pres4])
            db.session.commit()

            # Création des 4 clubs
            club_bde = Club(nom="BDE", description="Bureau des Étudiants - Animation de la vie estudiantine et organisation d'événements.", categorie="Vie Associative", date_creation="2024-01-01", president=pres1)
            club_mains = Club(nom="Les Mains Solidaires", description="Club dédié au volontariat, aux actions humanitaires et caritatives au sein de l'université.", categorie="Humanitaire", date_creation="2024-01-10", president=pres4)
            club_bleu = Club(nom="Bleu Hands", description="Club spécialisé dans l'industrie navale et la protection des écosystèmes marins.", categorie="Industrie/Environnement", date_creation="2024-02-01", president=pres2)
            club_tink = Club(nom="TinkCraft", description="Le pôle d'innovation en Intelligence Artificielle (AI) et technologies de pointe.", categorie="Intelligence Artificielle", date_creation="2024-02-15", president=pres3)
            
            for c, p in [(club_bde, pres1), (club_mains, pres4), (club_bleu, pres2), (club_tink, pres3)]:
                c.membres.append(p)
            
            db.session.add_all([club_bde, club_mains, club_bleu, club_tink])

            # Événements
            e1 = Evenement(titre="Intégration", date="2024-09-20", description="Fête.", adhesion="Payant", club=club_bde)
            e2 = Evenement(titre="Collecte", date="2024-10-05", description="Social.", adhesion="Gratuit", club=club_mains)
            db.session.add_all([e1, e2])

            db.session.commit()
            print("Clubs BDE, Les Mains Solidaires, Bleu Hands et TinkCraft créés !")

# ============================================================
# ROUTES (PAGES WEB)
# ============================================================

@app.route('/')
def index():
    user = session.get('user_email')
    clubs = Club.query.all()
    return render_template('index.html', clubs=clubs, user=user)

@app.route('/club/<int:club_id>')
def voir_club(club_id):
    club = db.session.get(Club, club_id)
    if not club:
        return "Club non trouvé", 404
    return render_template('club.html', club=club)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Requête dans la base de données
        user = Membre.query.filter_by(email=email, password=password).first()
        if user:
            session['user_email'] = user.email
            session['user_nom'] = f"{user.prenom} {user.nom}"
            session['user_id'] = user.id
            flash("Connexion réussie !", "success")
            return redirect(url_for('index'))
        else:
            flash("Email ou mot de passe incorrect.", "danger")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        password = request.form.get('password')
        filiere = request.form.get('filiere')
        telephone = request.form.get('telephone')
        
        # Vérifier si l'email existe déjà
        if Membre.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.", "danger")
            return redirect(url_for('register'))
        
        nouveau_membre = Membre(nom=nom, prenom=prenom, email=email, password=password, filiere=filiere, telephone=telephone)
        db.session.add(nouveau_membre)
        db.session.commit()
        
        flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/club/<int:club_id>/join', methods=['POST'])
def join_club(club_id):
    if 'user_id' not in session:
        flash("Vous devez être connecté pour rejoindre un club.", "danger")
        return redirect(url_for('login'))
        
    club = db.session.get(Club, club_id)
    user = db.session.get(Membre, session['user_id'])
    
    if club and user:
        if user not in club.membres:
            club.membres.append(user)
            db.session.commit()
            flash(f"Vous avez rejoint le {club.nom} !", "success")
        else:
            flash("Vous êtes déjà membre de ce club.", "info")
            
    return redirect(url_for('voir_club', club_id=club_id))

@app.route('/club/<int:club_id>/add_event', methods=['POST'])
def add_event(club_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    club = db.session.get(Club, club_id)
    # Vérification que l'utilisateur est bien le président du club
    if club and club.president_id == session['user_id']:
        titre = request.form.get('titre')
        date = request.form.get('date')
        description = request.form.get('description')
        adhesion = request.form.get('adhesion')
        
        nouvel_evenement = Evenement(titre=titre, date=date, description=description, adhesion=adhesion, club=club)
        db.session.add(nouvel_evenement)
        db.session.commit()
        
        flash("Événement ajouté avec succès.", "success")
    else:
        flash("Action non autorisée.", "danger")
        
    return redirect(url_for('voir_club', club_id=club_id))

@app.route('/club/<int:club_id>/remove_member/<int:membre_id>', methods=['POST'])
def remove_member(club_id, membre_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    club = db.session.get(Club, club_id)
    if club and club.president_id == session['user_id']:
        membre_a_supprimer = db.session.get(Membre, membre_id)
        if membre_a_supprimer and membre_a_supprimer in club.membres:
            club.membres.remove(membre_a_supprimer)
            db.session.commit()
            flash(f"Le membre {membre_a_supprimer.prenom} a été retiré.", "success")
    
    return redirect(url_for('voir_club', club_id=club_id))

@app.route('/logout')
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
