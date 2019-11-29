# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 11:20:45 2019

@author: USER
"""
import os
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QProgressBar
from models.exceptions import InvalidExtensionError, IncompleteInitialParameters, InvalidModelFile
from models.utilities import printProgressBar


class SambaModel():
    
    EXPECTED_INPUT_VARIABLES = ('day','month','year','J','Rain','ETo')
    EXTENSIONS = ('.xlsx','.xls')
    INITIAL_GENERATED_VARIABLES = ("Kc's",'Zr','TAW','RAW','PE')
    GENERATED_VARIABLES = INITIAL_GENERATED_VARIABLES + ('RunCte','Runoff','Ks','AWE','AE','NSS','SMD','Rec',"SMD'")
    FINAL_DAY = None
    
    def __init__(self,model_path,**kwargs):
        
        if os.path.splitext(model_path)[1] in self.EXTENSIONS:
            self.model = pd.read_excel(model_path) if pd.read_excel(model_path).iloc[0].all() else None   # checks if dummy row is appended to the model file              
            self.crop_stages = kwargs['crop_stages']
            self.max_root_depth = kwargs['max_root_depth']
            self.soil = kwargs['soil']
            self.crop_coefficient = kwargs['crop_coefficient']
            self.run_off_matrix = kwargs['run_off_matrix']
            self.model_constant_params = kwargs['model_constant_params']
            self.crop_duration = kwargs['crop_duration']
            
            
            if self.model is None:
                raise InvalidModelFile('Dummy row not appended to model file')
            else:
                self.FINAL_DAY = self.model.index[-1]
            
            # initializaing the dummy row in the dataframe
            for variable in self.GENERATED_VARIABLES:
                self.model[variable] = None
                self.model[variable][0] = 0
            
            
            # setting the initial smd value
            self.model["SMD'"][0] = self.model_constant_params['initial_smd']
            self.model["SMD'"][1] = self.model_constant_params['initial_smd']
        else:
            raise InvalidExtensionError('File extension invalid')
            
    
    def generate_model(self):
        
        print('Loading......')
        self.generate_initial_variables()
        
        try:
            for i in self.model.index:
                index = i+1
                printProgressBar(index,len(self.model.index),prefix = 'Progress:', suffix = 'Complete',length=50)
                self.model[self.GENERATED_VARIABLES[5]][index] = self.get_run_off_coefficient(index)
                self.model[self.GENERATED_VARIABLES[6]][index] = self.get_runoff(index)
                self.model[self.GENERATED_VARIABLES[7]][index] = self.get_ks(index)
                self.model[self.GENERATED_VARIABLES[8]][index] = self.get_average_water_evapotranspiration(index)
                self.model[self.GENERATED_VARIABLES[9]][index] = self.get_average_evatranspiration(index)
                self.model[self.GENERATED_VARIABLES[10]][index] = self.get_nss(index)
                self.model[self.GENERATED_VARIABLES[11]][index] = self.get_smd(index)
                self.model[self.GENERATED_VARIABLES[12]][index] = self.get_recharge(index)
                self.model[self.GENERATED_VARIABLES[13]][index+1] = self.get_smd_prime(index)                
        except Exception:
                pass
        finally:
                self.model[self.GENERATED_VARIABLES[5]][self.FINAL_DAY] = self.get_run_off_coefficient(self.FINAL_DAY)
                self.model[self.GENERATED_VARIABLES[6]][self.FINAL_DAY] = self.get_runoff(self.FINAL_DAY)
                self.model[self.GENERATED_VARIABLES[7]][self.FINAL_DAY] = self.get_ks(self.FINAL_DAY)
                self.model[self.GENERATED_VARIABLES[8]][self.FINAL_DAY] = self.get_average_water_evapotranspiration(self.FINAL_DAY)
                self.model[self.GENERATED_VARIABLES[9]][self.FINAL_DAY] = self.get_average_evatranspiration(self.FINAL_DAY)
                self.model[self.GENERATED_VARIABLES[10]][self.FINAL_DAY] = self.get_nss(self.FINAL_DAY)
                self.model[self.GENERATED_VARIABLES[11]][self.FINAL_DAY] = self.get_smd(self.FINAL_DAY)
                self.model[self.GENERATED_VARIABLES[12]][self.FINAL_DAY] = self.get_recharge(self.FINAL_DAY)
                
                # delete the first dummy row
                self.model = self.model.drop(self.model.index[0])
            
    def generate_initial_variables(self):
        
        
        '''
        This generates the variablels that are not dependent on initial SMD value
        
        @ variables
            - Kc's :
            - Zr   :
            - TAW  : Tatal Average Water
            - RAW  : 
            - PE   : Potential Evapotranspiration
        '''
        
        if set(self.EXPECTED_INPUT_VARIABLES).issubset(set(self.model.columns)):
            
            for variable_column in self.INITIAL_GENERATED_VARIABLES:                
                
                if variable_column == "Kc's":
                    julian_days  = self.model['J'].values
                    for index,julian_day in list(enumerate(julian_days)):
                        if self.crop_stages['planting']<= julian_day < self.crop_stages['development']:
                            self.model[variable_column][index] = self.crop_coefficient['middle']
                        elif self.crop_stages['development']<= julian_day < self.crop_stages['middle']:
                            self.model[variable_column][index] = self.crop_coefficient['initial']+(julian_day-self.crop_stages['development'])/self.crop_duration['development']*(self.crop_coefficient['middle']-self.crop_coefficient['initial'])
                        elif self.crop_stages['middle']<=julian_day<self.crop_stages['late']:
                            self.model[variable_column][index] = self.crop_coefficient['middle']
                        elif self.crop_stages['late']<= julian_day <= self.crop_stages['harvest']:
                            self.model[variable_column][index] = self.crop_coefficient['middle']+(julian_day-self.crop_stages['late'])/self.crop_duration['late']*(self.crop_coefficient['end']-self.crop_coefficient['middle'])
                        elif self.crop_stages['harvest']<=julian_day<self.crop_stages['harvest'] + 10:
                            self.model[variable_column][index] = self.crop_coefficient['end'] + (julian_day-self.crop_stages['harvest'])/10 * (self.crop_coefficient['bs']-self.crop_coefficient['end'])
                        else:
                            self.model[variable_column][index] = self.crop_coefficient['bs']
                
                if variable_column == 'Zr':
                    julian_days = self.model['J'].values
                    for index,julian_day in list(enumerate(julian_days)):
                        if julian_day <= self.crop_stages['planting']:
                            self.model[variable_column][index] = 0.0
                        elif self.crop_stages['planting'] < julian_day <= self.crop_stages['development']:
                            self.model[variable_column][index] = self.model_constant_params['Ze']
                        elif self.crop_stages['development'] < julian_day <= self.crop_stages['middle']:
                            self.model[variable_column][index] = self.model_constant_params['Ze'] + ((julian_day-self.crop_stages['development']))/self.crop_duration['development']*(self.max_root_depth-self.model_constant_params['Ze'])
                        else:
                            self.model[variable_column][index] = self.max_root_depth
                            
                if variable_column == 'TAW':
                    Zr = self.model['Zr'].values
                    index = self.model.index
                    for index, data in zip(index,Zr):
                        self.model[variable_column][index] =  max(((self.soil['FC']-self.soil['WP'])*1000*data),(self.soil['FC']-0.5*self.soil['WP'])*1000*self.model_constant_params['Ze'])
               
                if variable_column == 'RAW':
                    self.model[variable_column] = self.model['TAW']*self.model_constant_params['depletion_factor']
                    
                if variable_column == 'PE':
                     self.model[variable_column] = self.model["Kc's"]*self.model['ETo']
    
        else:
            raise IncompleteInitialParameters(message ='Incomplete initial parameter sets', param = None)

    
    def get_run_off_coefficient(self,index):        
        
        
        '''
        returns the runoff coefficient for a particular julian day 
        '''
        
        rainfall_intensity = self.model['Rain'][index]
        smd_prime = self.model["SMD'"][index]
        coefficient = None
        if rainfall_intensity < 20:
            if smd_prime < 20:
                coefficient = self.run_off_matrix[0,0]
            elif 20<= smd_prime <= 50:
                coefficient = self.run_off_matrix[0,1]
            else:
                coefficient =  self.run_off_matrix[0,2]
        elif 20 <= rainfall_intensity <= 50:
            if smd_prime < 20:
                coefficient = self.run_off_matrix[1,0]
            elif 20<= smd_prime <= 50:
                coefficient = self.run_off_matrix[1,1]
            else:
                coefficient =  self.run_off_matrix[1,2]
        else:
            if smd_prime < 20:
                coefficient = self.run_off_matrix[2,0]
            elif 20<= smd_prime <= 50:
                coefficient = self.run_off_matrix[2,1]
            else:
                coefficient =  self.run_off_matrix[2,2]
        
        return coefficient
        
    def get_runoff(self,index):
        
        '''
        returns the runoff for a particular julian day 
        '''
        
        rainfall_intensity = self.model['Rain'][index]
        runoff_coeff = self.model['RunCte'][index]
        return runoff_coeff*rainfall_intensity
    
    def get_ks(self,index):
        
        '''
        returns the Ks for a particular julian day 
        '''
        
        taw = self.model['TAW'][index]
        smd_prime = self.model["SMD'"][index]
        ks_value = None
        if smd_prime >= taw:
            ks_value = 0
                            
        elif smd_prime > taw * self.model_constant_params['depletion_factor']:
            ks_value = round((taw-smd_prime)/(taw-taw*self.model_constant_params['depletion_factor']),2)

        else:
            ks_value = 1
        
        return ks_value
    
    def get_average_water_evapotranspiration(self,index):
        
        
        '''
        returns the average water evapotranspiration for a particular julian day 
        '''
        
        rainfall_intensity = self.model['Rain'][index]
        runoff = self.model['Runoff'][index]
        nss = 0 if self.model['NSS'][index-1] is None else self.model['NSS'][index-1]
        smd_prime = self.model["SMD'"][index-1]
        awe_value = None
        
        if smd_prime > 0:
            awe_value = rainfall_intensity - runoff + nss
        else:
            awe_value = rainfall_intensity - runoff            
        return awe_value
        
        
    def get_average_evatranspiration(self,index):
        
        '''
        returns the average evapotranspiration for a particular julian day 
        '''
        
        
        awe_value = self.model['AWE'][index]
        pe_value  = self.model['PE'][index]
        taw_value = self.model['TAW'][index]
        ks_value = self.model['Ks'][index]
        smd_prime = self.model["SMD'"][index]
        depletion_factor = self.model_constant_params['depletion_factor']
        ae_value = None
        
        if smd_prime < taw_value * depletion_factor:
            ae_value = pe_value                            
        elif awe_value >= pe_value:
            ae_value = pe_value
        elif smd_prime >= taw_value :
            ae_value = awe_value
        elif smd_prime < taw_value:
            ae_value = awe_value + ks_value*(pe_value - awe_value)
            
        return ae_value
        
        
    def get_nss(self,index):
        
        '''
        returns the nss for a particular julian day 
        '''
        
        awe_value = self.model['AWE'][index]
        ae_value = self.model['AE'][index]
        smd_prime = self.model["SMD'"][index]
        nss_value = None
        nss_fraction = self.model_constant_params['nss_fraction']
        
        if awe_value - ae_value > smd_prime:
            nss_value = 0
        else:
            nss_value = max((awe_value-ae_value)*nss_fraction,0)
            
        return nss_value
    
    def get_smd(self,index):
        
        '''
        returns the smd value for a particular julian day 
        '''
        awe_value = self.model['AWE'][index]
        nss_value = self.model['NSS'][index]
        ae_value = self.model['AE'][index]
        smd_prime = self.model["SMD'"][index]       
        
        smd_value = smd_prime+ae_value - awe_value + nss_value
        return smd_value        
     
    def get_recharge(self,index):
        
        
        '''
        returns the recharge value for a particular julian day 
        '''
        
        smd_value = self.model['SMD'][index]
        nss_value = self.model['NSS'][index]
        recharge = None
        
        if smd_value < 0:
            recharge = ((-1)*smd_value)+nss_value
        else:
            recharge = 0
        
        return recharge
    
    def get_smd_prime(self,index):
        
        '''
        returns the smd for the next julian day 
        '''
        
        smd_prime = None
        smd_value = self.model['SMD'][index]
        recharge = self.model['Rec'][index]
        
        if smd_value < 0:
            smd_prime = 0
        else:
            smd_prime = smd_value + recharge
        
        return smd_prime
        
    def load_visualization(self,visualization_type):
        
        if visualization_type == 'SMD':
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
            months = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')
            
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        