#include <TMath.h>

#include "QualityController.h"

QualityController::QualityController() {
    ptMin = 0.4;
    ptMax = 2.0;
    yMin = 0.0;
    yMax = 0.5;
    mass2Min = 0.6;
    mass2Max = 1.2;
    lower_p0 = 0.780239;
    lower_p1 = 0.0342841;
    lower_p2 = -0.0218734;
    lower_trancate = 4.5;
    upper_p0 = 0.930886;
    upper_p1 = -0.0150339;
    upper_p2 = 0.0168854;
    fTofMassLower = new TF1("fLower", "pol2", 0, 10);
    fTofMassUpper = new TF1("fUpper", "pol2", 0, 10);
    isDefault = true;
}

void QualityController::ReadConfig(std::ifstream* ifConfig) {
    mIfConfig = ifConfig;
    if (!mIfConfig || !mIfConfig->is_open()) {
        std::cout << "[ERROR] - From QualityController Module: Loading hyperparams config failed.\n";
        exit(0);
    }
    std::cout << "[LOG] - From QualityController Module: Config file read in, now parsing...\n";

    while (!mIfConfig->eof()) {
        std::string types, val1, val2, val3, val4;
        *mIfConfig >> types;

        if (types == "VARLIST") { // just a header
            continue;
        } else if (types == "PT") {
            *mIfConfig >> val1 >> val2;
            ptMin = std::stod(val1);
            ptMax = std::stod(val2);
        } else if (types == "YP") {
            *mIfConfig >> val1 >> val2;
            yMin = std::stod(val1);
            yMax = std::stod(val2);
        } else if (types == "MASS2") {
            *mIfConfig >> val1 >> val2;
            mass2Min = std::stod(val1);
            mass2Max = std::stod(val2);
        } else if (types == "TOFHIGH") {
            *mIfConfig >> val1 >> val2 >> val3;
            upper_p0 = std::stod(val1);
            upper_p1 = std::stod(val2);
            upper_p2 = std::stod(val3);
        } else if (types == "TOFLOW") {
            *mIfConfig >> val1 >> val2 >> val3 >> val4;
            lower_p0 = std::stod(val1);
            lower_p1 = std::stod(val2);
            lower_p2 = std::stod(val3);
            lower_trancate = std::stod(val4);
        } else if (types == "END") {
            break;
        } else {
            std::cout << "[ERROR] - From QualityController Module: Invalid arugument (" << types << ").\n";
            exit(0);
        }
        isDefault = false;
    }
    // print
    std::cout << "[LOG] - From QualityController Module: Parameters read, here is the summary: \n";
    Print();
}

void QualityController::Print() {
    if (isDefault) {
        std::cout << "[LOG] - From QualityController Module: Using default cuts:\n";
    } else {
        std::cout << "[LOG] - From QualityController Module: Here are the cuts specified:\n";
    }

    std::cout << "=== Acceptance Cuts ===\n";
    std::cout << "= pt range: " << ptMin << " - " << ptMax << std::endl;
    std::cout << "= y (proton) range: " << yMin << " - " << yMax << std::endl;

    // === next few lines are using momentum-dependent mass cut
    // std::cout << "= m2 upper limit curve parameters: " << upper_p0 << " + " << upper_p1 << "*x + " << upper_p2 << "*x^2" << std::endl;
    // std::cout << "= m2 lower limit curve parameters: " << lower_p0 << " + " << lower_p1 << "*x + " << lower_p2 << "*x^2" << std::endl;
    // std::cout << "= m2 lower limit trancate at: " << lower_trancate << std::endl;
    // fTofMassLower->SetParameters(lower_p0, lower_p1, lower_p2);
    // fTofMassUpper->SetParameters(upper_p0, upper_p1, upper_p2);
    
    // === currently use hard cut
    std::cout << "= m2 lower cut at " << mass2Min << std::endl;
    std::cout << "= m2 upper cut at " << mass2Max << std::endl;

}

bool QualityController::Accept(float pt, float y, float p, float mass2) {
    if (pt < ptMin || pt > ptMax) { return false; }
    if (y < yMin || y > yMax) { return false; }
    return IsTofAccepted(p, mass2);
    return true;
}

bool QualityController::IsTofAccepted(float p, float mass2) {
    // if (fTofMassUpper->Eval(p) < mass2) { return false; }
    // if (p > lower_trancate) { p = lower_trancate; }
    // if (fTofMassLower->Eval(p) > mass2) { return false; }
    // return true;
    return mass2 > mass2Min && mass2 < mass2Max;
}