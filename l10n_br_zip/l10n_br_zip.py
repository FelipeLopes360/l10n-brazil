# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2012  Renato Lima (Akretion)                                  #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

import re
from openerp import models, api, fields
from openerp.exceptions import Warning


class L10n_brZip(models.Model):
    """ Este objeto persiste todos os códigos postais que podem ser
    utilizados para pesquisar e auxiliar o preenchimento dos endereços.
    """
    _name = 'l10n_br.zip'
    _description = 'CEP'
    _rec_name = 'zip'
    
    zip = fields.Char(string='CEP', size=8, required=True)
    street_type = fields.Char(string='Tipo', size=26)
    street = fields.Char(string='Logradouro', size=72)
    district = fields.Char(string='Bairro', size=72)
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one(
            'res.country.state', string='Estado',
            domain="[('country_id','=',country_id)]")
    l10n_br_city_id = fields.Many2one(
            'l10n_br_base.city', string='Cidade',
            required=True, domain="[('state_id','=',state_id)]")
    

    def set_domain(self, country_id=False, state_id=False,
                l10n_br_city_id=False, district=False,
                street=False, zip_code=False):
        domain = []
        if zip_code:
            new_zip = re.sub('[^0-9]', '', zip_code or '')
            domain.append(('zip', '=', new_zip))
        else:
            if not state_id or not l10n_br_city_id or \
                len(street or '') == 0:
                raise Warning(
                    u'Parametros insuficientes',
                    u'Necessário informar Estado, município e logradouro')

            if country_id:
                domain.append(('country_id', '=', country_id))
            if state_id:
                domain.append(('state_id', '=', state_id))
            if l10n_br_city_id:
                domain.append(('l10n_br_city_id', '=', l10n_br_city_id))
            if district:
                domain.append(('district', 'like', district))
            if street:
                domain.append(('street', 'like', street))

        return domain
    
    def set_result(self, zip_read=None):
        if zip_read:
            zip_code = zip_read['zip']
            if len(zip_code) == 8:
                zip_code = '%s-%s' % (zip_code[0:5], zip_code[5:8])
            result = {
                'country_id': zip_read['country_id'] and zip_read['country_id'].id or False,
                'state_id': zip_read['state_id'] and zip_read['state_id'].id or False,
                'l10n_br_city_id': zip_read['l10n_br_city_id'] and zip_read['l10n_br_city_id'].id or False,
                'district': (zip_read['district'] or ''),
                'street': ((zip_read['street_type'] or '') + ' ' + (zip_read['street'] or '')),
                'zip': zip_code,
            }
        else:
            result = {}
        return result

    @api.multi
    def zip_search_multi(self, country_id=False,
                        state_id=False, l10n_br_city_id=False,
                        district=False, street=False, zip_code=False):
        domain = self.set_domain(
            country_id=country_id,
            state_id=state_id,
            l10n_br_city_id=l10n_br_city_id,
            district=district,
            street=street,
            zip_code=zip_code)
        return self.search(domain)
    
    @api.multi
    def zip_search(self):
        result = self.set_result()
        zip_id = self.zip_search_multi(
            cr, uid, ids, context,
            country_id, state_id,
            l10n_br_city_id, district,
            street, zip_code)
        if len(zip_id) == 1:
            result = self.set_result(cr, uid, ids, context, zip_id[0])
            return result
        else:
            return False
    
    def create_wizard(self, object_name, country_id=False,
                    state_id=False, l10n_br_city_id=False,
                    district=False, street=False, zip_code=False,
                    zip_ids=False):

        context = {
            'zip': zip_code,
            'street': street,
            'district': district,
            'country_id': country_id,
            'state_id': state_id,
            'l10n_br_city_id': l10n_br_city_id,
            'zip_ids': list(zip_ids.ids),
            'address_id': self.id,
            'object_name': object_name }

        result = {
            'name': 'Zip Search',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_br.zip.search',
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
        }

        return result
