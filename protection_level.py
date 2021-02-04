"""
Author: Luca Battistella
Name : wdpa_country_processing
Group : wdpa
With QGIS : 31415
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterDefinition
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsProperty
import processing


class Wdpa_country_processing(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('inputcountries', 'Input Countries or EEZ', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputwdpapoints', 'Input wdpa points', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputwdpapolygons', 'Input wdpa polygons', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        param = QgsProcessingParameterString('wdpaversionperc', 'Postgres Table Name', multiLine=False, defaultValue='api_terr_jan_2021')
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        self.addParameter(QgsProcessingParameterFeatureSink('Result', 'result', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(23, model_feedback)
        results = {}
        outputs = {}

        # Reproject countries
        alg_params = {
            'INPUT': parameters['inputcountries'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectCountries'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Reproject layer
        alg_params = {
            'INPUT': parameters['inputwdpapolygons'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectLayer'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Reproject points
        alg_params = {
            'INPUT': parameters['inputwdpapoints'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectPoints'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Extracted points
        alg_params = {
            'INPUT': outputs['ReprojectPoints']['OUTPUT'],
            'INTERSECT': outputs['ReprojectCountries']['OUTPUT'],
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractedPoints'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extracted polygons
        alg_params = {
            'INPUT': outputs['ReprojectLayer']['OUTPUT'],
            'INTERSECT': outputs['ReprojectCountries']['OUTPUT'],
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractedPolygons'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'radius',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'sqrt(  \"REP_AREA\"/3.14)',
            'INPUT': outputs['ExtractedPoints']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': '\"STATUS\"   =  \'Designated\'\r\nor  \"STATUS\"  = \'Inscribed\'\r\n or \"STATUS\"  = \'Adopted\'\r\nor  \"STATUS\"  = \'Eestablished\' ',
            'INPUT': outputs['ExtractedPolygons']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': QgsProperty.fromExpression('"radius"*1000'),
            'END_CAP_STYLE': 0,
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Fix EXTRACTED
        alg_params = {
            'INPUT': outputs['ExtractByExpression']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixExtracted'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Fix BUFFER
        alg_params = {
            'INPUT': outputs['Buffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixBuffer'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Dissolve BUFFERED POINTS
        alg_params = {
            'FIELD': 'ISO3',
            'INPUT': outputs['FixBuffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolveBufferedPoints'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Dissolve POLYGONS
        alg_params = {
            'FIELD': 'ISO3',
            'INPUT': outputs['FixExtracted']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolvePolygons'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Merged Protection
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:54009'),
            'LAYERS': [outputs['DissolveBufferedPoints']['OUTPUT'],outputs['DissolvePolygons']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergedProtection'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Fix merged points and polygons
        alg_params = {
            'INPUT': outputs['MergedProtection']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixMergedPointsAndPolygons'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Dissolve protection
        alg_params = {
            'FIELD': 'ISO3',
            'INPUT': outputs['FixMergedPointsAndPolygons']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolveProtection'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Fix dissolved protection
        alg_params = {
            'INPUT': outputs['DissolveProtection']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixDissolvedProtection'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Clip
        alg_params = {
            'INPUT': outputs['FixDissolvedProtection']['OUTPUT'],
            'OVERLAY': outputs['ReprojectCountries']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Clip'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Calculate clipped area
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_area',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': ' $area ',
            'INPUT': outputs['Clip']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateClippedArea'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Join geometries with attributes
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'isoa3_id',
            'FIELDS_TO_COPY': ['prot_area'],
            'FIELD_2': 'ISO3',
            'INPUT': outputs['ReprojectCountries']['OUTPUT'],
            'INPUT_2': outputs['CalculateClippedArea']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinGeometriesWithAttributes'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Calculate country area
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'country_area_km',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '\"country_area\"/1000000',
            'INPUT': outputs['JoinGeometriesWithAttributes']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateCountryArea'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Calculate protection
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_km',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '\"prot_area\"/1000000',
            'INPUT': outputs['CalculateCountryArea']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateProtection'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Calculate protection percentage
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_perc',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '(\"prot_km\"*100)/\"country_area_km\"',
            'INPUT': outputs['CalculateProtection']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': parameters['Result']
        }
        outputs['CalculateProtectionPercentage'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Result'] = outputs['CalculateProtectionPercentage']['OUTPUT']

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Export to PostgreSQL
        alg_params = {
            'CREATEINDEX': True,
            'DATABASE': 'Biopama_api',
            'DROP_STRING_LENGTH': False,
            'ENCODING': 'UTF-8',
            'FORCE_SINGLEPART': False,
            'GEOMETRY_COLUMN': 'geom',
            'INPUT': outputs['CalculateProtectionPercentage']['OUTPUT'],
            'LOWERCASE_NAMES': True,
            'OVERWRITE': False,
            'PRIMARY_KEY': '',
            'SCHEMA': 'protection_level',
            'TABLENAME': parameters['wdpaversionperc']
        }
        outputs['ExportToPostgresql'] = processing.run('qgis:importintopostgis', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'wdpa_country_processing'

    def displayName(self):
        return 'wdpa_country_processing'

    def group(self):
        return 'wdpa'

    def groupId(self):
        return 'wdpa'

    def createInstance(self):
        return Wdpa_country_processing()
