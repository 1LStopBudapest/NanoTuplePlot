import math

USE_GENPARTFLAV_MATCHING = False  # True: old genPartFlav-based truth matching, False: DeltaR-based truth matching

# the codes start at 1 so that the first bin of the histogram stays empty and
# can be seen, bin 0 is easy to misread
ORIGIN_CODES = {
    'not_from_stop':     1,   # the walk never reaches a stop
    'W_leptonic':        2,   # lepton straight from the leptonic W leg
    'W_leptonic_tau':    3,   # leptonic W leg, but through a tau
    'stop_b':            4,   # bare b quark seen, so the b comes from the stop
    'W_hadronic':        5,   # from the hadronic products of the W leg
    'stop_2body':        6,   # from a 2 body (stop -> c chi0) leg
    'maybe_from_stop_b': 7,   # b hadron but no bare b quark, chain is pruned
    'unclassified':      8,   # nothing matched, should stay empty
}

# a lepton counts as truth matched only if it comes from the leptonic W leg
SIGNAL_ORIGINS = ('W_leptonic', 'W_leptonic_tau')


def is_bare_b(pdgid):
    """True only for the bare b quark."""
    return abs(pdgid) == 5


def is_bottom_hadron(pdgid):
    """True for b flavoured mesons (511, 513, 521, ...) and baryons (5122, ...)."""
    a = abs(pdgid)
    return (a/100) % 10 == 5 or (a/1000) % 10 == 5


def is_charm_hadron(pdgid):
    """True for c flavoured mesons (411, 413, 421, ...) and baryons (4122, ...)."""
    a = abs(pdgid)
    return (a/100) % 10 == 4 or (a/1000) % 10 == 4


def is_hadron(pdgid):
    """
    True for mesons and baryons. Quarks, leptons and bosons are all below 100
    and the SUSY particles start at 1000001, so a plain range test is enough.
    """
    a = abs(pdgid)
    return a >= 100 and a < 1000000


class LeptonTruthMatcher(object):
    """
    Truth-matches a reconstructed lepton (typically the leading selected
    lepton) to a generated lepton descending from a stop, and classifies
    where in the stop decay chain that generated lepton came from.

    Extracted from
    NanoTuplePlot/CutFlow_study_LL/FillHistos_test_lepton_truth.py so it can
    be reused standalone in another FillHistos-style script.

    Usage per event (after tree.GetEntry(i)):

        matcher = LeptonTruthMatcher(tree)
        sorted_leps = getsel.getSortedLepVar()
        if len(sorted_leps) > 0:
            reco = sorted_leps[0]   # leading reco lepton dict
            truth_matched, matched_gen_lep, best_deltaR = matcher.match(reco)
            if matched_gen_lep is not None:
                origin = matched_gen_lep["origin"]         # e.g. 'W_leptonic'
                code   = ORIGIN_CODES[origin]              # to fill a histo

    reco is expected to be a dict with keys 'eta', 'phi', 'pt', 'type', 'idx'
    -- exactly the shape TreeVarSel(_LL).getSortedLepVar() returns, where
    'type' is one of 'mu', 'Electron', 'LowPtElectron'.

    NOTE: matched_gen_lep is None both in genPartFlav mode and when no gen
    lepton of the same flavour was found, so always check it before using it,
    even when truth_matched is True.
    """

    def __init__(self, tree, stop_pdgId=1000006, max_steps=200,
                 deltaR_max=0.01, pt_cut_gen=1, eta_cut_gen=2.5):
        self.tree = tree
        self.stop_pdgId = stop_pdgId
        self.max_steps = max_steps
        self.deltaR_max = deltaR_max
        self.pt_cut_gen = pt_cut_gen
        self.eta_cut_gen = eta_cut_gen

    def get_stop_ancestry(self, gen_lep, print_parents=False):
        """
        Walks upwards through mother indices and collects the pdgId of every
        ancestor that is crossed on the way up.
        Returns (stop_pdg, chain), where stop_pdg is the SIGNED pdgId of the
        stop the walk ended on (+1000006 stop, -1000006 anti-stop), or 0 if no
        stop was reached, and chain is the list of pdgIds that were crossed.
        A lepton comes from the stop if stop_pdg is not 0.
        """
        tree = self.tree
        chain = []
        current_idx = gen_lep["genIdx"]
        steps = 0
        if print_parents:
            print("lepton inheritance:")
        while current_idx >= 0 and steps < self.max_steps:
            pdgid = tree.GenPart_pdgId[current_idx]
            chain.append(pdgid)
            if print_parents:
                print("pdgid = "+str(pdgid))

            if abs(pdgid) == self.stop_pdgId:
                return pdgid, chain

            current_idx = tree.GenPart_genPartIdxMother[current_idx]
            steps += 1
        return 0, chain

    def leg_is_2body(self, stop_pdg):
        """
        Decay mode of the leg the lepton came from, read from the
        stopDecay/stopAntiDecay branches (>3.5 = 4 body, <3.5 = 2 body).
        NOTE: still to be checked on the samples which branch goes with which sign.
        """
        tree = self.tree
        branch = 'stopDecay' if stop_pdg > 0 else 'stopAntiDecay'
        if not hasattr(tree, branch):
            return False
        return getattr(tree, branch) < 3.5

    def classify_origin(self, gen_lep):
        """
        Classifies where a generated lepton comes from inside the stop decay
        chain. Returns one of the keys of ORIGIN_CODES, testing in this order:

          0 chain never reaches a stop                          -> not_from_stop
          1 leg is 2 body                                       -> stop_2body
          2 no hadron in the chain, tau present                 -> W_leptonic_tau
          3 no hadron in the chain, no tau                      -> W_leptonic
          4 hadron present, W (+-24) in the chain               -> W_hadronic
          5 hadron present, no W, bare b quark in the chain     -> stop_b
          6 hadron present, no W, b hadron only                 -> maybe_from_stop_b
          7 hadron present, no W, c hadron                      -> W_hadronic
          8 hadron present, no W, light hadron                  -> W_hadronic
          9 nothing above matched                               -> unclassified
        """
        stop_pdg, chain = self.get_stop_ancestry(gen_lep)

        if stop_pdg == 0:
            return 'not_from_stop'

        if self.leg_is_2body(stop_pdg):
            return 'stop_2body'

        hadrons = [p for p in chain if is_hadron(p)]

        # nothing hadronic in between, so this is the leptonic W leg
        if len(hadrons) == 0:
            for p in chain:
                if abs(p) == 15:
                    return 'W_leptonic_tau'
            return 'W_leptonic'

        # a hadron sits in between, so the lepton is a hadron decay product

        # the W is visible above the hadron, so the hadron comes from the W
        for p in chain:
            if abs(p) == 24:
                return 'W_hadronic'

        # the bare b quark is still in the record, so the b comes from the stop
        for p in chain:
            if is_bare_b(p):
                return 'stop_b'

        # b hadron but the bare b quark was pruned away, cannot tell for sure
        for p in hadrons:
            if is_bottom_hadron(p):
                return 'maybe_from_stop_b'

        # no b anywhere, so the charm comes from the hadronic W leg
        for p in hadrons:
            if is_charm_hadron(p):
                return 'W_hadronic'

        # light hadron, same assumption as for the charm
        for p in hadrons:
            if not is_bottom_hadron(p) and not is_charm_hadron(p):
                return 'W_hadronic'

        return 'unclassified'

    def get_final_gen_leptons(self):
        """
        Builds the list of final-state gen leptons (status==1, e/mu/tau,
        pt/eta cuts) for the currently loaded tree entry, each tagged with
        its origin bucket and whether it descends from the stop.
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
            gen_lep["origin"] = self.classify_origin(gen_lep)
            gen_lep["originCode"] = ORIGIN_CODES[gen_lep["origin"]]
            gen_lep["fromStop"] = gen_lep["origin"] != 'not_from_stop'

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
        The lepton counts as truth matched only if the gen lepton it matches
        comes from the leptonic W leg (SIGNAL_ORIGINS).
        In genPartFlav mode, matched_gen_lep and best_deltaR are None.
        The matched gen lepton carries 'origin'/'originCode'/'fromStop'.
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
            truth_matched_lepton = matched_gen_lep["origin"] in SIGNAL_ORIGINS
        else:
            truth_matched_lepton = False

        return truth_matched_lepton, matched_gen_lep, best_deltaR
