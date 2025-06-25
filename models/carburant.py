# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class Carburant(models.Model):
    _name = 'parc.automobile.carburant'
    _description = "Suivi de consommation carburant"
    _inherit = ['mail.thread']
    _order = 'date_plein desc'
    
    name = fields.Char(string="Référence", compute="_compute_name", store=True, index=True)
    vehicule_id = fields.Many2one('parc.automobile.voiture', string="Véhicule", required=True, 
                                 ondelete='cascade', tracking=True)
    
    # Informations du plein
    date_plein = fields.Date(string="Date du plein", required=True, 
                            default=fields.Date.today, tracking=True)
    type_carburant = fields.Selection([
        ('essence', 'Essence'),
        ('diesel', 'Diesel'),
        ('electrique', 'Électrique'),
        ('hybride', 'Hybride'),
        ('gpl', 'GPL')
    ], string="Type de carburant", required=True, default='essence')
    
    # Quantités et prix
    quantite = fields.Float(string="Quantité (L)", required=True, digits=(8, 2))
    prix_unitaire = fields.Float(string="Prix/L", required=True, digits=(8, 3))
    montant_total = fields.Float(string="Montant total", compute="_compute_montant_total", 
                                store=True, digits=(10, 2))
    
    # Kilométrage
    kilometrage_actuel = fields.Float(string="Kilométrage actuel", required=True, digits=(10, 2))
    kilometrage_precedent = fields.Float(string="Kilométrage précédent", 
                                        compute="_compute_kilometrage_precedent", digits=(10, 2))
    distance_parcourue = fields.Float(string="Distance parcourue (km)", 
                                     compute="_compute_distance_parcourue", 
                                     store=True, digits=(10, 2))
    
    # Consommation
    consommation = fields.Float(string="Consommation (L/100km)", 
                               compute="_compute_consommation", 
                               store=True, digits=(4, 2))
    est_anomalie = fields.Boolean(string="Anomalie détectée", 
                                 compute="_compute_anomalie", store=True)
    
    # Informations complémentaires
    station_service = fields.Char(string="Station-service")
    plein_complet = fields.Boolean(string="Plein complet", default=True)
    commentaire = fields.Text(string="Commentaire")
    facture = fields.Binary(string="Facture")
    facture_filename = fields.Char(string="Nom de la facture")
    
    @api.depends('vehicule_id', 'date_plein')
    def _compute_name(self):
        for record in self:
            if record.vehicule_id and record.date_plein:
                record.name = f"Plein {record.vehicule_id.name} - {record.date_plein}"
            else:
                record.name = "Nouveau plein"
    
    @api.depends('quantite', 'prix_unitaire')
    def _compute_montant_total(self):
        for record in self:
            record.montant_total = record.quantite * record.prix_unitaire
    
    @api.depends('vehicule_id', 'date_plein', 'kilometrage_actuel')
    def _compute_kilometrage_precedent(self):
        for record in self:
            if record.vehicule_id and record.date_plein:
                precedent = self.search([
                    ('vehicule_id', '=', record.vehicule_id.id),
                    ('date_plein', '<', record.date_plein),
                    ('id', '!=', record.id)
                ], limit=1, order='date_plein desc')
                record.kilometrage_precedent = precedent.kilometrage_actuel if precedent else 0
            else:
                record.kilometrage_precedent = 0
    
    @api.depends('kilometrage_actuel', 'kilometrage_precedent')
    def _compute_distance_parcourue(self):
        for record in self:
            if record.kilometrage_actuel and record.kilometrage_precedent:
                if record.kilometrage_actuel >= record.kilometrage_precedent:
                    record.distance_parcourue = record.kilometrage_actuel - record.kilometrage_precedent
                else:
                    record.distance_parcourue = 0
            else:
                record.distance_parcourue = 0
    
    @api.depends('quantite', 'distance_parcourue', 'plein_complet')
    def _compute_consommation(self):
        for record in self:
            if (record.distance_parcourue > 0 and record.quantite > 0 and 
                record.plein_complet):
                record.consommation = (record.quantite * 100) / record.distance_parcourue
            else:
                record.consommation = 0
    
    @api.depends('consommation', 'vehicule_id')
    def _compute_anomalie(self):
        for record in self:
            if record.vehicule_id and record.consommation > 0:
                # Calculer la consommation moyenne des 5 derniers pleins
                derniers_pleins = self.search([
                    ('vehicule_id', '=', record.vehicule_id.id),
                    ('consommation', '>', 0),
                    ('id', '!=', record.id)
                ], limit=5, order='date_plein desc')
                
                if len(derniers_pleins) >= 3:
                    moyenne = sum(derniers_pleins.mapped('consommation')) / len(derniers_pleins)
                    # Anomalie si écart > 25% de la moyenne
                    record.est_anomalie = abs(record.consommation - moyenne) > (moyenne * 0.25)
                else:
                    record.est_anomalie = False
            else:
                record.est_anomalie = False
    
    @api.constrains('kilometrage_actuel', 'vehicule_id')
    def _check_kilometrage_coherent(self):
        for record in self:
            if record.vehicule_id and record.kilometrage_actuel:
                # Vérifier que le kilométrage n'est pas inférieur au précédent
                precedent = self.search([
                    ('vehicule_id', '=', record.vehicule_id.id),
                    ('date_plein', '<', record.date_plein),
                    ('id', '!=', record.id)
                ], limit=1, order='date_plein desc')
                
                if precedent and record.kilometrage_actuel < precedent.kilometrage_actuel:
                    raise ValidationError(_("Le kilométrage actuel (%s km) ne peut pas être inférieur au kilométrage précédent (%s km)") % 
                                        (record.kilometrage_actuel, precedent.kilometrage_actuel))
