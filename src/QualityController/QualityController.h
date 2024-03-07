/*

    Version 2.0 (15.01.2024)

    > Now TOF mass cut is changed -> p-dependent
    
    Version 1.0 (08.09.2023)

    > First version for CBM in virgo server.

*/

#ifndef __YIGE_QLT_CTRL__
#define __YIGE_QLT_CTRL__

#include <fstream>
#include <iostream>
#include <string>

#include "TF1.h"

class QualityController {

    private:
        std::ifstream* mIfConfig;
        // quality cuts are fixed:
        // - see MyAnalysisCuts.h
        // Here only consider analysis cuts (acceptance cuts)
        float ptMin;
        float ptMax;
        float yMin;
        float yMax;
        float mass2Min;
        float mass2Max;
        bool isDefault;
        float lower_p0, upper_p0, lower_p1, upper_p1, lower_p2, upper_p2;
        float lower_trancate;
        TF1* fTofMassUpper;
        TF1* fTofMassLower;

    public:
        QualityController();
        ~QualityController(){}

        void ReadConfig(std::ifstream* ifConfig);
        void Print();
        // bool Accept(float pt, float y, float mass2);
        bool Accept(float pt, float y, float p, float mass2);
        bool IsTofAccepted(float p, float mass2);

};

#endif
