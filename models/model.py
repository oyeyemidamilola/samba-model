# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 20:56:17 2019

@author: USER
"""

import pandas as pd
import numpy as np
import os
from models.exceptions import InvalidExtensionError, IncompleteInitialParameters


class Model():
    
    MODEL_VARIABLES = ['RunCte','Runoff',"Kc's",'Zr','TAW','RAW','PE','Ks','AE','SMD','Rec']
    INITIAL_MODEL_VARIABLES = ['day','month','year','J','Rain','ETo',"SMD'",'AWE','NSS']
    EXTENSIONS = ['.csv','.xlsx','.xls'] 
    #CROP_DURATION = {'initial':60,'development':90,'middle':100,'late':100}
    max_root_depth = None
    
    
    def __init__(self,model_path,**kwargs):
        
        if os.path.splitext(model_path)[1] in self.EXTENSIONS:
            self.model = pd.read_excel(model_path)
            self.crop_stages = kwargs['crop_stages']
            self.max_root_depth = kwargs['max_root_depth']
            self.soil = kwargs['soil']
            self.crop_coefficient = kwargs['crop_coefficient']
            self.run_off_matrix = kwargs['run_off_matrix']
            self.model_constant_params = kwargs['model_constant_params']
            self.crop_duration = kwargs['crop_duration']
                
        else:
            raise InvalidExtensionError('File extension invalid') 
            
    def generate_model(self):
        
        if self.INITIAL_MODEL_VARIABLES == list(self.model.columns):
            for new_column in self.MODEL_VARIABLES:
                if new_column == 'Zr':
                    self.model[new_column] = None
                    julian_days = self.model['J'].values
                    for index,julian_day in list(enumerate(julian_days)):
                        if julian_day <= self.crop_stages['planting']:
                            self.model[new_column][index] = 0.0
                        elif self.crop_stages['planting'] < julian_day <= self.crop_stages['development']:
                            self.model[new_column][index] = self.model_constant_params['Ze']
                        elif self.crop_stages['development'] < julian_day <= self.crop_stages['middle']:
                            self.model[new_column][index] = self.model_constant_params['Ze'] + ((julian_day-self.crop_stages['development']))/self.crop_duration['development']*(self.max_root_depth-self.model_constant_params['Ze'])
                        else:
                            self.model[new_column][index] = self.max_root_depth
                
                if new_column == "Kc's":
                    self.model[new_column] = None
                    julian_days  = self.model['J'].values
                    for index,julian_day in list(enumerate(julian_days)):
                        if self.crop_stages['planting']<= julian_day < self.crop_stages['development']:
                            self.model[new_column][index] = self.crop_coefficient['middle']
                        elif self.crop_stages['development']<= julian_day < self.crop_stages['middle']:
                            self.model[new_column][index] = self.crop_coefficient['initial']+(julian_day-self.crop_stages['development'])/self.crop_duration['development']*(self.crop_coefficient['middle']-self.crop_coefficient['initial'])
                        elif self.crop_stages['middle']<=julian_day<self.crop_stages['late']:
                            self.model[new_column][index] = self.crop_coefficient['middle']
                        elif self.crop_stages['late']<= julian_day <= self.crop_stages['harvest']:
                            self.model[new_column][index] = self.crop_coefficient['middle']+(julian_day-self.crop_stages['late'])/self.crop_duration['late']*(self.crop_coefficient['end']-self.crop_coefficient['middle'])
                        elif self.crop_stages['harvest']<=julian_day<self.crop_stages['harvest'] + 10:
                            self.model[new_column][index] = self.crop_coefficient['end'] + (julian_day-self.crop_stages['harvest'])/10 * (self.crop_coefficient['bs']-self.crop_coefficient['end'])
                        else:
                            self.model[new_column][index] = self.crop_coefficient['bs']
                    
                if new_column == 'TAW':
                    self.model[new_column] = None
                    Zr = self.model['Zr'].values
                    index = self.model.index
                    for index, data in zip(index,Zr):
                        self.model[new_column][index] =  max(((self.soil['FC']-self.soil['WP'])*1000*data),(self.soil['FC']-0.5*self.soil['WP'])*1000*self.model_constant_params['Ze'])
               
                if new_column == 'RAW':
                    self.model[new_column] = self.model['TAW']*self.model_constant_params['depletion_factor']  
                
                if new_column == 'PE':
                    self.model[new_column] = self.model["Kc's"]*self.model['ETo']
                if new_column == 'RunCte':
                    rainfall_intensity = self.model['Rain']
                    smd_values = self.model["SMD'"]
                    index = self.model.index
                    self.model[new_column] = None
                    for index,intensity,smd in zip(index,rainfall_intensity,smd_values):
                        if intensity < 20:
                            if smd < 20 :
                                self.model[new_column][index] = self.run_off_matrix[0,0]
                            elif 20<= smd <= 50:
                                self.model[new_column][index] = self.run_off_matrix[0,1]
                            else:
                                self.model[new_column][index] = self.run_off_matrix[0,2]
                        elif 20<= intensity <= 50:
                            if smd < 20 :
                                self.model[new_column][index] = self.run_off_matrix[1,0]
                            elif 20<= smd <= 50:
                                self.model[new_column][index] = self.run_off_matrix[1,1]
                            else:
                                self.model[new_column][index] = self.run_off_matrix[1,2]
                        else:
                            if smd < 20 :
                                self.model[new_column][index] = self.run_off_matrix[2,0]
                            elif 20<= smd <= 50:
                                self.model[new_column][index] = self.run_off_matrix[2,1]
                            else:
                                self.model[new_column][index] = self.run_off_matrix[2,2]
                
                if new_column == 'Runoff':
                    self.model[new_column] = self.model['Rain']*self.model['RunCte']
               
                if new_column == 'Ks':
                    self.model[new_column] = None
                    taw_values = self.model['TAW']
                    smd_values = self.model["SMD'"]
                    index = self.model.index
                    for index,taw,smd in zip(index,taw_values,smd_values):
                        if smd >= taw:
                            self.model[new_column][index] = 0
                            
                        elif smd > taw * self.model_constant_params['depletion_factor']:
                            self.model[new_column][index] = round((taw-smd)/(taw-taw*self.model_constant_params['depletion_factor']),2)

                        else:
                            self.model[new_column][index] = 1
                            
                if new_column == 'AE':
                    self.model[new_column] = None
                    index = self.model.index
                    awe_values = self.model['AWE']
                    pe_values = self.model['PE']
                    taw_values = self.model['TAW']
                    Ks_values = self.model['Ks']
                    smd_values = self.model["SMD'"]
                    depletion_factor = self.model_constant_params['depletion_factor']
                    
                    for index,awe,pe,taw,ks,smd in zip(index,awe_values,pe_values,taw_values,Ks_values,smd_values):
                        if smd < taw * depletion_factor:
                            self.model[new_column][index] = pe
                            
                        if awe >= pe:
                            self.model[new_column][index] = pe
                            
                        if smd >= taw :
                            self.model[new_column][index] = awe
                        if smd < taw:
                            self.model[new_column][index] = awe + ks*(pe - awe)
                    
                if new_column == 'SMD':
                    self.model[new_column] = self.model["SMD'"]+self.model['AE'] - self.model['AWE']+self.model['NSS']
                
                if new_column == 'Rec':
                    self.model[new_column] = None
                    smd_values = self.model['SMD']
                    nss_values = self.model['NSS']
                    index = self.model.index
                    
                    for index,smd,nss in zip(index,smd_values,nss_values):
                        if smd < 0:
                            self.model[new_column][index] = ((-1)*smd)+nss
                        else:
                            self.model[new_column][index] = 0
    
    def load_visualization(self,visualization_type):
        
        if visualization_type == 'SMB':
            julian_days = self.model['J'].values
            runoff = self.model['Runoff'].values
            taw = self.model['TAW'].values
            smd = self.model['SMD'].values
            rainfall = self.model['Rain'].values
            
            return { 'visualization_type':visualization_type,
                    'julian_days':julian_days,
                    'runoff':runoff,
                    'taw':taw,
                    'smd':smd,
                    'rainfall':rainfall}
        
        
        elif visualization_type == 'Monthly precipitation' :
            monthly_precipitation = {}
            months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            
            for index, month in enumerate(months):
                monthly_precipitation[month] = sum(self.model.loc[self.model['month'] == index + 1].Rain)
            
            y_pos = np.arange(len(months))
            
            return {'visualization_type':visualization_type,
                    'months':months,
                    'y_pos':y_pos,
                    'monthly_precipitation':monthly_precipitation}
        
        
        elif visualization_type == 'Evapotranspiration':
            julian_days = self.model['J'].values
            eto = self.model['ETo'].values
            pe = self.model['PE'].values
            ae = self.model['AE'].values
            
            return{'visualization_type':visualization_type,
                   'julian_days':julian_days,
                   'eto':eto,
                   'pe':pe,
                   'ae':ae}
        elif visualization_type == 'Recharge/Runoff':
            julian_days = self.model['J'].values
            recharge = self.model['Rec'].values
            runoff = self.model['Runoff'].values
            
            return {'visualization_type':visualization_type,
                    'julian_days':julian_days,
                    'recharge':recharge,
                    'runoff':runoff}
        else:
            raise IncompleteInitialParameters(message ='Incomplete initial parameter sets', param = None)
        
         
        