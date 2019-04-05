import FWCore.ParameterSet.Config as cms

XMLIdealGeometryESSource = cms.ESSource("XMLIdealGeometryESSource",
    geomXMLFiles = cms.vstring(        
        'Geometry/CMSCommonData/data/materials.xml',
        'Geometry/CMSCommonData/data/rotations.xml',
        'gemqc8/Geometry/data/cms.xml',
        #'Geometry/MuonCommonData/data/GEMQC8/muonBase.xml', # Phase-2 Muon
        #'Geometry/MuonCommonData/data/GEMQC8/cmsMuon.xml',        
        #'Geometry/MuonCommonData/data/GEMQC8/mf.xml',        
        'gemqc8/Geometry/data/gemf/TDR_BaseLine/gemf.xml',
        'gemqc8/Geometry/data/gem11.xml',
        'gemqc8/Geometry/data/muonNumbering.xml',
        'gemqc8/Geometry/data/muonSens.xml',
        'gemqc8/Geometry/data/muonProdCuts.xml',
        'gemqc8/Geometry/data/GEMSpecsFilter.xml',   # Phase-2 Muon
        'gemqc8/Geometry/data/GEMSpecs.xml',
        'gemqc8/Geometry/data/gembox.xml',
        ## these are added on the fly
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c1_r1.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c1_r2.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c1_r3.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c1_r4.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c1_r5.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c2_r1.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c2_r2.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c2_r3.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c2_r4.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c2_r5.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c3_r1.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c3_r2.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c3_r3.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c3_r4.xml',
        ## 'Geometry/MuonCommonData/data/GEMQC8/gem11L_c3_r5.xml',

        ),
    rootNodeName = cms.string('cms:OCMS')
)

