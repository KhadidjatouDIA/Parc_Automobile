# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class Voiture(models.Model):
    _name = 'parc.automobile.voiture'
    _description = "Véhicule du parc automobile"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    # Informations de base
    name = fields.Char(string='Nom', required=True, tracking=True)
    photo = fields.Binary(string='Photo')
    immatriculation = fields.Char(string='Immatriculation', required=True, index=True, tracking=True)
    numero_chassis = fields.Char(string="Numéro de châssis", required=True, index=True)
    
    # Classification
    type_vehicule = fields.Selection([
        ('voiture', 'Voiture'),
        ('utilitaire', 'Utilitaire'),
        ('moto', 'Moto'),
        ('camion', 'Camion')
    ], string="Type de véhicule", required=True, default='voiture', tracking=True)
    
    couleur = fields.Selection([
        ('blanc', 'Blanc'),
        ('noir', 'Noir'),
        ('gris', 'Gris'),
        ('rouge', 'Rouge'),
        ('bleu', 'Bleu'),
        ('vert', 'Vert'),
        ('jaune', 'Jaune'),
        ('autre', 'Autre')
    ], string='Couleur', required=True, default='blanc')
    
    # Dates importantes
    date_acquisition = fields.Date(string="Date d'acquisition", required=True, tracking=True)
    date_service = fields.Date(string="Date de mise en service", tracking=True)
    
    # État et kilométrage
    etat = fields.Selection([
        ('neuf', 'Neuf'),
        ('service', 'En service'),
        ('maintenance', 'En maintenance'),
        ('hs', 'Hors service'),
        ('vendu', 'Vendu'),
        ('reforme', 'Réformé')
    ], string='État', required=True, default='service', tracking=True)
    
    kilometrage = fields.Float(string='Kilométrage actuel', digits=(10, 2), tracking=True)
    centre_service = fields.Char(string="Centre/Service affecté")
    
    # Relations
    modele_id = fields.Many2one('parc.automobile.modele', string="Modèle", required=True, ondelete='restrict')
    marque_id = fields.Many2one(related='modele_id.marque_id', string="Marque", store=True, readonly=True)
    carte_grise_id = fields.Many2one('parc.automobile.carte.grise', string="Carte grise")
    assurance_id = fields.Many2one('parc.automobile.assurance', string="Assurance")
    
    # Relations avec les autres modèles
    affectation_ids = fields.One2many('parc.automobile.affectation', 'vehicule_id', string="Affectations")
    entretien_ids = fields.One2many('parc.automobile.entretien', 'voiture_id', string="Entretiens")
    carburant_ids = fields.One2many('parc.automobile.carburant', 'vehicule_id', string="Suivi carburant")
    document_ids = fields.One2many('parc.automobile.document', 'vehicule_id', string="Documents")
    notification_ids = fields.One2many('parc.automobile.notification', 'vehicule_id', string="Notifications")
    
    # Champs calculés
    affectation_actuelle_id = fields.Many2one('parc.automobile.affectation', 
                                             string="Affectation actuelle", 
                                             compute="_compute_affectation_actuelle")
    
    consommation_moyenne = fields.Float(string="Consommation moyenne (L/100km)", 
                                       compute="_compute_consommation_moyenne", 
                                       store=True)
    
    cout_entretien_annuel = fields.Float(string="Coût entretien annuel", 
                                        compute="_compute_cout_entretien_annuel")
    
    nb_entretiens = fields.Integer(string="Nombre d'entretiens", 
                                  compute="_compute_nb_entretiens")
    
    date_dernier_entretien = fields.Date(string="Dernier entretien", 
                                        compute="_compute_dernier_entretien")
    
    prochain_entretien = fields.Date(string="Prochain entretien prévu", 
                                    compute="_compute_prochain_entretien")
    
    # Informations administratives
    documents_a_renouveler = fields.Integer(string="Documents à renouveler", 
                                           compute="_compute_documents_a_renouveler")
    
    active = fields.Boolean(string="Actif", default=True)
    description = fields.Text(string='Description')
    
    @api.depends('affectation_ids.statut', 'affectation_ids.date_fin')
    def _compute_affectation_actuelle(self):
        for record in self:
            affectation_active = record.affectation_ids.filtered(
                lambda a: a.statut == 'active' and (not a.date_fin or a.date_fin >= fields.Date.today())
            )
            record.affectation_actuelle_id = affectation_active[0] if affectation_active else False
    
    @api.depends('carburant_ids.consommation')
    def _compute_consommation_moyenne(self):
        for record in self:
            consommations = record.carburant_ids.filtered(lambda c: c.consommation > 0).mapped('consommation')
            record.consommation_moyenne = sum(consommations) / len(consommations) if consommations else 0
    
    def _compute_cout_entretien_annuel(self):
        for record in self:
            current_year = date.today().year
            entretiens_annee = record.entretien_ids.filtered(
                lambda e: e.date_entretien and e.date_entretien.year == current_year
            )
            record.cout_entretien_annuel = sum(entretiens_annee.mapped('cout'))
    
    def _compute_nb_entretiens(self):
        for record in self:
            record.nb_entretiens = len(record.entretien_ids)
    
    def _compute_dernier_entretien(self):
        for record in self:
            dernier = record.entretien_ids.filtered('date_entretien').sorted('date_entretien', reverse=True)
            record.date_dernier_entretien = dernier[0].date_entretien if dernier else False
    
    def _compute_prochain_entretien(self):
        for record in self:
            prochain = record.entretien_ids.filtered(lambda e: e.statut == 'planifie').sorted('date_entretien')
            record.prochain_entretien = prochain[0].date_entretien if prochain else False
    
    def _compute_documents_a_renouveler(self):
        for record in self:
            today = fields.Date.today()
            dans_30_jours = today + timedelta(days=30)
            docs_a_renouveler = record.document_ids.filtered(
                lambda d: d.date_expiration and d.date_expiration <= dans_30_jours
            )
            record.documents_a_renouveler = len(docs_a_renouveler)
    
    @api.constrains('immatriculation')
    def _check_immatriculation_unique(self):
        for record in self:
            if record.immatriculation:
                existing = self.search([
                    ('immatriculation', '=', record.immatriculation),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_("L'immatriculation %s existe déjà pour le véhicule %s") % 
                                        (record.immatriculation, existing[0].name))
    
    @api.constrains('numero_chassis')
    def _check_chassis_unique(self):
        for record in self:
            if record.numero_chassis:
                existing = self.search([
                    ('numero_chassis', '=', record.numero_chassis),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_("Le numéro de châssis %s existe déjà pour le véhicule %s") % 
                                        (record.numero_chassis, existing[0].name))
