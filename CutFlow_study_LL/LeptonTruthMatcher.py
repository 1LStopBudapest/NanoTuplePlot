import math

USE_GENPARTFLAV_MATCHING = False  # True: old genPartFlav-based truth matching, False: DeltaR-based truth matching

class LeptonTruthMatcher(object):
    """
    Truth-matches a reconstructed lepton (typically the leading selected
    lepton) to a generated lepton descending from a stop, extracted from
    NanoTuplePlot/CutFlow_study_LL/FillHistos_test_lepton_truth.py so it can
    be reused standalone in another FillHistos-style script.

    Usage per event (after tree.GetEntry(i)):

        matcher = LeptonTruthMatcher(tree)
        sorted_leps = getsel.getSortedLepVar()
        if len(sorted_leps) > 0:
            reco = sorted_leps[0]   # leading reco lepton dict
            truth_matched, matched_gen_lep, best_deltaR = matcher.match(reco)

    reco is expected to be a dict with keys 'eta', 'phi', 'pt', 'type', 'idx'
    -- exactly the shape TreeVarSel(_LL).getSortedLepVar() returns, where
    'type' is one of 'mu', 'Electron', 'LowPtElectron'.
    """

    def __init__(self, tree, stop_pdgId=1000006, max_steps=20,
                 deltaR_max=0.01, pt_cut_gen=1, eta_cut_gen=2.5):
        self.tree = tree
        self.stop_pdgId = [stop_pdgId, -stop_pdgId]
        self.max_steps = max_steps
        self.deltaR_max = deltaR_max
        self.pt_cut_gen = pt_cut_gen
        self.eta_cut_gen = eta_cut_gen

    def is_from_stop(self, gen_lep, print_parents=False):
        """
        Walks upwards through mother indices to see if this gen lepton
        originates from the stop (or antistop).
        """
        tree = self.tree
        current_idx = gen_lep["genIdx"]
        steps = 0
        if print_parents:
            print("lepton inheritance:")
        while current_idx >= 0 and steps < self.max_steps:
            pdgid = tree.GenPart_pdgId[current_idx]
            if print_parents:
                print("pdgid = "+str(pdgid))

            # If we reach a stop, this lepton is from the signal
            if abs(pdgid) in self.stop_pdgId:
                return True

            # Move to mother
            current_idx = tree.GenPart_genPartIdxMother[current_idx]
            steps += 1
        return False

    def get_final_gen_leptons(self):
        """
        Builds the list of final-state gen leptons (status==1, e/mu/tau,
        pt/eta cuts) for the currently loaded tree entry, each tagged with
        whether it descends from the stop.
        """
        tree = self.tree
        final_leptons = []

        for i in range(tree.nGenPart):
            pdgid = tree.GenPart_pdgId[i]
            status = tree.GenPart_status[i]
            pt = tree.GenPart_pt[i]
            eta = tree.GenPart_eta[i]

            if (status == 1 and
                abs(pdgid) in (11, 13, 15)
                and pt > self.pt_cut_gen
                and abs(eta) < self.eta_cut_gen):

                final_leptons.append({
                    "pdgId": pdgid,
                    "pt": pt,
                    "eta": tree.GenPart_eta[i],
                    "phi": tree.GenPart_phi[i],
                    "mass": tree.GenPart_mass[i],
                    "genIdx": i,
                })

        for gen_lep in final_leptons:
            gen_lep["fromStop"] = self.is_from_stop(gen_lep)

        return final_leptons

    def _get_genPartFlav(self, reco_type, reco_idx):
        tree = self.tree
        if reco_type == 'mu':
            return ord(tree.Muon_genPartFlav[reco_idx]) if hasattr(tree, 'Muon_genPartFlav') else -1
        elif reco_type == 'Electron':
            return ord(tree.Electron_genPartFlav[reco_idx]) if hasattr(tree, 'Electron_genPartFlav') else -1
        else:
            return ord(tree.LowPtElectron_genPartFlav[reco_idx]) if hasattr(tree, 'LowPtElectron_genPartFlav') else -1

    def match(self, reco_lepton):
        """
        reco_lepton: dict with keys 'eta','phi','pt','type','idx' for the
        reconstructed lepton to truth-match (see class docstring).

        Returns (truth_matched_lepton, matched_gen_lep, best_deltaR).
        In genPartFlav mode, matched_gen_lep and best_deltaR are None.
        """
        reco_eta = reco_lepton.get('eta', 0.0)
        reco_phi = reco_lepton.get('phi', 0.0)
        tp = reco_lepton['type']
        reco_idx = reco_lepton['idx']

        final_leptons = self.get_final_gen_leptons()

        if USE_GENPARTFLAV_MATCHING:
            old_flag = self._get_genPartFlav(tp, reco_idx)
            truth_matched_lepton = old_flag in [1, 15]
            return truth_matched_lepton, None, None

        # === DeltaR matching loop ===
        best_deltaR = 999.0
        matched_gen_lep = None

        for gen_lep in final_leptons:
            # Simple flavor check first
            if (tp == 'mu' and abs(gen_lep["pdgId"]) != 13) or \
               (tp != 'mu' and abs(gen_lep["pdgId"]) != 11):
                continue

            d_eta = reco_eta - gen_lep["eta"]
            d_phi = reco_phi - gen_lep["phi"]
            # Correct phi difference for 2pi periodicity
            d_phi = (d_phi + math.pi) % (2 * math.pi) - math.pi

            deltaR = math.sqrt(d_eta*d_eta + d_phi*d_phi)

            if deltaR < best_deltaR:
                best_deltaR = deltaR
                matched_gen_lep = gen_lep

        if matched_gen_lep is not None and best_deltaR < self.deltaR_max:
            truth_matched_lepton = matched_gen_lep["fromStop"]
        else:
            truth_matched_lepton = False

        return truth_matched_lepton, matched_gen_lep, best_deltaR
