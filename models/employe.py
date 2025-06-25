# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Employe(models.Model):
    _name = 'parc.automobile.employe'
    _description = "Employé pouvant utiliser les véhicules"
    _order = 'name'
    
    name = fields.Char(string='Nom complet', compute='_compute_name', store=True, index=True)
    prenom = fields.Char(string='Prénom', required=True)
    nom = fields.Char(string='Nom de famille', required=True)
    numero_employe = fields.Char(string="Numéro d'employé", index=True)
    
    # Coordonnées
    adresse = fields.Text(string='Adresse')
    telephone = fields.Char(string='Téléphone')
    email = fields.Char(string='E-mail')
    
    # Informations professionnelles
    poste = fields.Char(string='Poste')
    departement = fields.Char(string='Département')
    date_embauche = fields.Date(string="Date d'embauche", required=True)
    manager_id = fields.Many2one('parc.automobile.employe', string="Manager")
    
    # Permis et autorisations
    permis_conduire = fields.Boolean(string="Permis de conduire", default=True)
    date_permis = fields.Date(string="Date d'obtention du permis")
    categories_permis = fields.Char(string="Catégories de permis (B, C, D...)")
    autorisation_vehicule_service = fields.Boolean(string="Autorisé à utiliser les véhicules de service", default=True)
    
    # Relations
    affectation_ids = fields.One2many('parc.automobile.affectation', 'employe_id', string="Affectations")
    
    # Champs calculés
    affectation_actuelle_id = fields.Many2one('parc.automobile.affectation', 
                                             string="Affectation actuelle", 
                                             compute="_compute_affectation_actuelle")
    
    nb_affectations = fields.Integer(string="Nombre d'affectations", compute="_compute_nb_affectations")
    active = fields.Boolean(string="Actif", default=True)
    
    @api.depends('prenom', 'nom')
    def _compute_name(self):
        for record in self:
            if record.prenom and record.nom:
                record.name = f"{record.prenom} {record.nom}"
            else:
                record.name = record.prenom or record.nom or ""
    
    @api.depends('affectation_ids.statut', 'affectation_ids.date_fin')
    def _compute_affectation_actuelle(self):
        for record in self:
            affectation_active = record.affectation_ids.filtered(
                lambda a: a.statut == 'active' and (not a.date_fin or a.date_fin >= fields.Date.today())
            )
            record.affectation_actuelle_id = affectation_active[0] if affectation_active else False
    
    def _compute_nb_affectations(self):
        for record in self:
            record.nb_affectations = len(record.affectation_ids)

