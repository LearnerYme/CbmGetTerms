// std headers
#include <iostream>
#include <vector>
#include <string>
#include "assert.h" 

// root headers
#include "TFile.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TEfficiency.h"

// AnalysisTree headers
#include "BranchConfig.hpp"
#include "Configuration.hpp"
#include "DataHeader.hpp"
#include "EventHeader.hpp"
#include "Detector.hpp"
#include "Matching.hpp"
#include "Track.hpp"
#include "Chain.hpp"

// additional module headers
#include "IdxConstants/IdxConstants.h"
#include "DuplicateRemover/DuplicateRemover.h"
#include "MultiplicityTool/MultiplicityTool.h"
#include "CentralityTool/CentralityTool.h"
#include "CentralityTool/CentParams.h"
#include "CbmCut/CbmCut.h"
#include "QualityController/QualityController.h"
#include "Loader/Loader.h"
#include "EffMaker/EffMaker.h"

using std::vector;
using std::string;

using namespace AnalysisTree;

using std::cout;
using std::endl;

// main

int main(int argc, char** argv) {

	Chain t(
		vector<string>({"file.list"}),
		vector<string>({"rTree"})
	);
	float BeamRapidity = 1.62179;

	Configuration* cfg = t.GetConfiguration();

	// 
    EventHeader* mSimEventHeader = new EventHeader();
    EventHeader* mRecEventHeader = new EventHeader();
    Particles* mSimTracks = new Particles();
    HitDetector* mTofHits = new HitDetector();
    TrackDetector* mVtxTracks = new TrackDetector();

	// mathing between detectors
	Matching* mMatchingVtx2Sim = new Matching();
    Matching* mMatchingVtx2Tof = new Matching();
    Matching* mMatchingTof2Sim = new Matching();

	// set branch for detectors and matchings
	t.SetBranchAddress("VtxTracks2SimParticles.", &mMatchingVtx2Sim);
    t.SetBranchAddress("VtxTracks2TofHits.", &mMatchingVtx2Tof);
    t.SetBranchAddress("TofHits2SimParticles.", &mMatchingTof2Sim);
    t.SetBranchAddress("RecEventHeader.", &mRecEventHeader);  
    t.SetBranchAddress("SimEventHeader.", &mSimEventHeader);  
    t.SetBranchAddress("SimParticles.", &mSimTracks);
    t.SetBranchAddress("VtxTracks.", &mVtxTracks);  
    t.SetBranchAddress("TofHits.", &mTofHits);  

	// parse arguments
	const char* eff_path = argv[1];
	const char* task_tag = argv[2];
	double eff_factor = atof(argv[3]);
	int mainMode = atoi(argv[4]);
	cout << "[LOG] Now parsing input arguments..." << endl;
	cout << "[LOG] = Efficiency file path: " << eff_path << endl;
	cout << "[LOG] = Task tag: " << task_tag << endl;
	cout << "[LOG] = Efficiency factor: " << eff_factor << endl;
	cout << "[LOG] = Main mode: " << mainMode << endl;
	// about main mode: 
	// 	-> 0 for PhQMD MC, using RefMult3M
	// 	-> 1 for reconstructed, using RefMult3
	// 	-> 2 for reconstructed, BUT using RefMult3M
	assert(mainMode >= 0 && mainMode <= 2);
	assert(eff_factor >= 0.0 && eff_factor <= 1.0);
	
	// multiplicity tool
	cout << "[LOG] Loading modules: MultiplicityTool" << endl;
	MultiplitityTool* mMultTool = new MultiplitityTool();
	mMultTool->Init();
	mMultTool->EnableMc(true);
	
	// duplicated MC particle remover
	cout << "[LOG] Loading modules: DuplicateRemover" << endl;
	DuplicateRemover* mDupRmver = new DuplicateRemover();
	mDupRmver->Init();

	// centrality tool
	cout << "[LOG] Loading modules: CentralityTool" << endl;
	CentralityTool* mCentTool = new CentralityTool();
	mCentTool->ReadParams();

	// cbm cut
	cout << "[LOG] Loading modules: MyCbmCut" << endl;
	MyCbmCut* mCut = new MyCbmCut();
	mCut->Enable(true);

	// efficiency tool
	cout << "[LOG] Loading modules: EffMaker" << endl;
	EffMaker* mEff = new EffMaker();
	mEff->ReadInEffFile(eff_path);

	// quality control tool
	cout << "[LOG] Loading modules: QualityController" << endl;
	QualityController* mQc = new QualityController();
	std::ifstream* fin = new std::ifstream();
	fin->open(Form("%s.getTerms.cfg", task_tag));
	mQc->ReadConfig(fin);

	// terms loader
	cout << "[LOG] Loading modules: Loader" << endl;
	const int mMaxMult = 510; // for Loader
	Loader* lder = new Loader("Pro", mMaxMult);

	// prepare histogram
	cout << "[LOG] Setting up histograms" << endl;
	TH2F* hNpVsMult = new TH2F(
		"hNpVsMult", ";Multiplicity;N_{proton}",
		mMaxMult, -0.5, mMaxMult-0.5,
		100, -0.5, 99.5
	);
	TH2F* hNpVsCent = new TH2F(
		"hNpVsCent", ";Centrality;N_{proton}",
		cent_conf::nCentrality, -0.5, cent_conf::nCentrality-0.5,
		100, -0.5, 99.5
	);
	const char* centName[cent_conf::nCentrality] = {
        "0-10%", "10-20%",
        "20-30%", "30-40%", "40-50%",
    };
    for (int i=0; i<5; i++) {
        hNpVsCent->GetXaxis()->SetBinLabel(i+1, centName[i]);
    }

    cout << "[LOG] Everything is set up, now I'm going to start" << endl;
	const int nEv = t.GetEntries();
    cout << "[LOG] There will be " << nEv << " events" << endl;
	// event loop starts
	for (auto iEv=0; iEv<nEv; iEv++) {
		t.GetEntry(iEv);
		if (iEv % 2000 == 0) {
			cout << "[LOG] Status report: " << iEv << " events of " << nEv << " processed" << endl;
		}
		if (!mCut->IsGoodEvent(*mRecEventHeader)) { continue; }
		mMultTool->Make(mVtxTracks, mTofHits, mMatchingVtx2Tof, mSimTracks);
		int mult, centrality;
		if (mainMode == 0 || mainMode == 2) { // PhQMD + rec. with RefMult3M
			mult = mMultTool->GetRefMult3M();
			centrality = mCentTool->GetCentrality(mult, true);
		} else if (mainMode == 1) { // rec.
			mult = mMultTool->GetRefMult3();
			centrality = mCentTool->GetCentrality(mult, false);
		}
		if (centrality < 0) { continue; }

		int np = 0;
		if (mainMode == 0) {
			// for PhQMD
			mDupRmver->Clear();
			for (const auto& McTrack : *mSimTracks) {
				if (!mCut->IsPrimarySimParticle(McTrack)) { continue; }
				if (McTrack.GetPid() != 2212) { continue; }
				if (mDupRmver->Make(McTrack)) { continue; }
				float McP = McTrack.GetP();
				float McPt = McTrack.GetPt();
				float McRap = McTrack.GetRapidity();
				McRap -= BeamRapidity; // boost to CoM frame
				if (!mQc->Accept(McPt, McRap, McP, 1.0)) { continue; } // this will always pass
				np ++;
				lder->ReadTrack(1.0, 1.0);
			}
		} else {
			// for 
			for (auto const& VtxTrack : *mVtxTracks) {
				const int cVtxId = VtxTrack.GetId();
				if (!mCut->IsGoodVtxTrack(VtxTrack)) { continue; }
				const int cMatchedTofId = mMatchingVtx2Tof->GetMatch(cVtxId);
				if (cMatchedTofId < 0) { continue; }
				const auto& TofHit = mTofHits->GetChannel(cMatchedTofId);
				if (!mCut->IsGoodTofHit(TofHit)) { continue; }
				float VtxPt = VtxTrack.GetPt();
				float VtxP = VtxTrack.GetP();
				float VtxRapLab = VtxTrack.GetRapidityByMass(0.938272);
				float VtxRapCm = VtxRapLab - BeamRapidity;
				float TofMass2 = TofHit.GetField<float>(IdxTofMass2);
				if (!mQc->Accept(VtxPt, VtxRapCm, VtxP, TofMass2)) { continue; }
				np ++;
				float eff = mEff->GetEfficiency(VtxPt, VtxRapCm, centrality);
				eff *= eff_factor;
				eff = eff > 1.0 ? 1.0 : eff;
				lder->ReadTrack(1.0, eff);
			}
		}
		lder->Store(mult);
		hNpVsMult->Fill(mult, np);
		hNpVsCent->Fill(centrality, np);
	}

	// save terms
	cout << "[LOG] Now saving terms into " << task_tag << ".root" << endl;
	lder->Save(Form("%s.root", task_tag));

	// save heat map
	cout << "[LOG] Now saving histograms" << endl;
	TFile* pDistFile = new TFile(Form("%s.pDist.root", task_tag), "recreate");
	pDistFile->cd();
	hNpVsMult->Write();
	hNpVsCent->Write();
	pDistFile->Close();

	cout << "[LOG] Everything is done, and this is the end of GetTerms!" << endl;

	return 0;
}
