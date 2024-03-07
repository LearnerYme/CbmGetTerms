/*

    Version 1.1 (03.03.2024)

    > With new format of effiicency file

    Version 1.0 (08.09.2023)

    > First version for CBM in virgo server.

*/

#include "EffMaker.h"
#include "TH2F.h"
#include "TFile.h"
#include "TString.h"
#include <iostream>
#include "string.h"

void EffMaker::ReadInEffFile(const char* eff_root_file_path) {
    if (!strcmp(eff_root_file_path, "none")) { // efficiency correction off
        IsCorr = false;
        return;
    }
    IsCorr = true;
    TFile* tf = new TFile(eff_root_file_path);
    std::cout << "[LOG] - From EffMaker Module: Efficiency root file path: " << eff_root_file_path << ".\n";

    for (int i=0; i<nCent; i++) {
        tf->GetObject(Form("Eff_cent%d", i), eff[i]);
    }

    return;
}

float EffMaker::GetEfficiency(float pt, float y, int centrality) {
    if (!IsCorr) { return 1.0; }
    if (centrality < 0 || centrality >= nCent) { return -1; }
    int x1 = eff[centrality]->GetXaxis()->FindBin(y);
    int x2 = eff[centrality]->GetYaxis()->FindBin(pt);
    float epsilon = eff[centrality]->GetBinContent(x1, x2);
    if (epsilon < 0 || epsilon > 1) { return -1; }
    return epsilon;
}
