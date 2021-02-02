from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Wdpa_country_processing(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('inputwdpapoints', 'Input wdpa points', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputwdpapolygons', 'Input wdpa polygons', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputcountries', 'Input Countries or EEZ', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Result', 'result', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(21, model_feedback)
        results = {}
        outputs = {}

        # Extracted polygons
        alg_params = {
            'INPUT': parameters['inputwdpapolygons'],
            'INTERSECT': parameters['inputcountries'],
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractedPolygons'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extracted points
        alg_params = {
            'INPUT': parameters['inputwdpapoints'],
            'INTERSECT': parameters['inputcountries'],
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractedPoints'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Reproject points
        alg_params = {
            'INPUT': outputs['ExtractedPoints']['OUTPUT'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:3857'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectPoints'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'radius',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'sqrt(  \"REP_AREA\"/3.14)',
            'INPUT': outputs['ReprojectPoints']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Reproject layer
        alg_params = {
            'INPUT': outputs['ExtractedPolygons']['OUTPUT'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:3857'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectLayer'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': '\"STATUS\"   =  \'Designated\'\r\nor  \"STATUS\"  = \'Inscribed\'\r\n or \"STATUS\"  = \'Adopted\'\r\nor  \"STATUS\"  = \'Eestablished\' ',
            'INPUT': outputs['ReprojectLayer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
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

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Fix EXTRACTED
        alg_params = {
            'INPUT': outputs['ExtractByExpression']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixExtracted'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Fix BUFFER
        alg_params = {
            'INPUT': outputs['Buffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixBuffer'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Dissolve BUFFERED POINTS
        alg_params = {
            'FIELD': 'ISO3',
            'INPUT': outputs['FixBuffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolveBufferedPoints'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Dissolve POLYGONS
        alg_params = {
            'FIELD': 'ISO3',
            'INPUT': outputs['FixExtracted']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolvePolygons'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # protection
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:3857'),
            'LAYERS': [outputs['DissolveBufferedPoints']['OUTPUT'],outputs['DissolvePolygons']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Protection'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Fix geometries
        alg_params = {
            'INPUT': outputs['Protection']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Dissolved protection
        alg_params = {
            'FIELD': 'ISO3',
            'INPUT': outputs['FixGeometries']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolvedProtection'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # fixed diss prot
        alg_params = {
            'INPUT': outputs['DissolvedProtection']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixedDissProt'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Clip
        alg_params = {
            'INPUT': outputs['FixedDissProt']['OUTPUT'],
            'OVERLAY': parameters['inputcountries'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Clip'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Country_protection_area
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
        outputs['Country_protection_area'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Join attributes country prot meters
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'isoa3_id',
            'FIELDS_TO_COPY': 'prot_area',
            'FIELD_2': 'ISO3',
            'INPUT': parameters['inputcountries'],
            'INPUT_2': outputs['Country_protection_area']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesCountryProtMeters'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # country_area_km
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'country_area_km',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '\"country_area\"/1000000',
            'INPUT': outputs['JoinAttributesCountryProtMeters']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Country_area_km'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # prot_area_km
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_area_km',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '\"prot_area\"/1000000',
            'INPUT': outputs['Country_area_km']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Prot_area_km'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_perc',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '(\"prot_area_km\"*100)/\"country_area_km\"',
            'INPUT': outputs['Prot_area_km']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': parameters['Result']
        }
        outputs['FieldCalculator'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Result'] = outputs['FieldCalculator']['OUTPUT']
        return results

    def name(self):
        return 'wdpa_country_processing'

    def displayName(self):
        return 'wdpa_country_processing'

    def group(self):
        return 'wdpa'

    def groupId(self):
        return ''

    def createInstance(self):
        return Wdpa_country_processing()
