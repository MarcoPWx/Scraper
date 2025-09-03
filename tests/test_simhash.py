import tempfile
from scraper.harvesters.massive import MassiveHarvester


def test_simhash_hamming_distance_behaves():
    with tempfile.TemporaryDirectory() as td:
        h = MassiveHarvester(output_dir=td)
        a = "Kubernetes manages containerized workloads and services"
        b = "Kubernetes orchestrates containers and services"
        c = "Redis is an in-memory data structure store"
        ha = h._simhash64(a)
        hb = h._simhash64(b)
        hc = h._simhash64(c)
        ab = h._hamming(ha, hb)
        ac = h._hamming(ha, hc)
        # Similar phrases should be closer than dissimilar ones
        assert ab < ac
        # And generally below the default threshold for near-duplicates (8)
        assert ab < 16

