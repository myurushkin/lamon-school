/**
 * Research publications by BroutonLab team members.
 * Pulled from broutonlab.com/research (2026-05-14). Sorted newest-first.
 *
 * Note: one entry on the source page had a swapped title — skipped here.
 * If you find more publications, add them at the top and keep chronological
 * order within years.
 */

export type Publication = {
  title: string;
  authors: string;
  venue: string;
  year: number;
  url: string;
};

export const publications: Publication[] = [
  {
    title: "Building Interpretable Feature Representations for Resume–Vacancy Matching by Distilling Production LLM Signals",
    authors: "Ilya Chekin, Vyacheslav Malyugin, Vladimir Chirkov, Mikhail Yurushkin",
    venue: "Conference on Empirical Methods in Natural Language Processing (EMNLP), Industry Track",
    year: 2026,
    url: "https://aclanthology.org/2026.emnlp-industry.71/",
  },
  {
    title: "Automated Corn Kernel Counting from Multiple Views",
    authors: "M.V. Yurushkin, A.A. Gornostal, P.V. Babich, R.F. Domingues, H.C.R.M. Catão, et al.",
    venue: "International Conference on Intelligent Information Technologies for Industry (IITI)",
    year: 2025,
    url: "https://link.springer.com/chapter/10.1007/978-3-032-13612-1_3",
  },
  {
    title: "Minimal String Search Under Regular Constraints",
    authors: "M.V. Yurushkin, I.A. Slynko, S.S. Bachurin",
    venue: "International Conference on Intelligent Information Technologies for Industry (IITI)",
    year: 2025,
    url: "",
  },
  {
    title: "Structural peculiarities of tandem repeats and their clinical significance",
    authors: "S.S. Bachurin, M.V. Yurushkin, I.A. Slynko, M.E. Kletskii, O.N. Burov, et al.",
    venue: "Biochemical and Biophysical Research Communications (Elsevier), vol. 692, 149349",
    year: 2024,
    url: "https://doi.org/10.1016/j.bbrc.2023.149349",
  },
  {
    title: "Principal Colors Extraction Using Topological Data Analysis",
    authors: "A. Kovalenko, D. Zadorozhniy, M. Yurushkin",
    venue: "Future of Information and Communication Conference (FICC), Springer",
    year: 2022,
    url: "https://doi.org/10.1007/978-3-030-98012-2_6",
  },
  {
    title: "Multi-label Classification Based on Domain Analysis in Fixed Point Method",
    authors: "Anna Berger, Sergey Guda",
    venue: "28th Conference of Open Innovations Association (FRUCT)",
    year: 2021,
    url: "https://ieeexplore.ieee.org/document/9347583/",
  },
  {
    title: "Threshold optimization for F measure of macro-averaged precision and recall",
    authors: "Anna Berger, Sergey Guda",
    venue: "Pattern Recognition (Elsevier), vol. 102",
    year: 2020,
    url: "https://doi.org/10.1016/j.patcog.2020.107250",
  },
  {
    title: "Numerical method for finding Nash and Stackelberg equilibria in river water quality control models",
    authors: "M.A. Reshitko, G.A. Ougolnitsky, A.B. Usov",
    venue: "Computer Research and Modeling, vol. 12",
    year: 2020,
    url: "https://doi.org/10.20537/2076-7633-2020-12-3-653-667",
  },
  {
    title: "Optimization and parallelization of simplified Balas' and Christofides' algorithm for the Traveling Salesman Problem",
    authors: "Victor Burkhovetskiy",
    venue: "Program Systems: Theory and Applications, vol. 11",
    year: 2020,
    url: "https://doi.org/10.25209/2079-3316-2020-11-4-3-16",
  },
  {
    title: "Detection of nucleotide sequences capable of forming non-canonical DNA structures: Application of automata theory",
    authors: "M.V. Yurushkin, L.R. Gervich, S.S. Bachurin, M.E. Kletskii",
    venue: "Computational Biology and Chemistry (Elsevier), vol. 80",
    year: 2019,
    url: "https://doi.org/10.1016/j.compbiolchem.2019.04.009",
  },
  {
    title: "Experimental Analysis of Approaches to Multidimensional Conditional Density Estimation",
    authors: "Anna Berger, Sergey Guda",
    venue: "AIST — Analysis of Images, Social Networks and Texts (Springer LNCS vol. 11832)",
    year: 2019,
    url: "https://doi.org/10.1007/978-3-030-37334-4_3",
  },
  {
    title: "Image clustering by autoencoders",
    authors: "A.S. Kovalenko, Y.M. Demyanenko",
    venue: "Information Technology and Nanotechnology (ITNT-2019)",
    year: 2019,
    url: "http://ceur-ws.org/Vol-2391/paper33.pdf",
  },
  {
    title: "An exact parallel algorithm for the Traveling Salesman Problem",
    authors: "Victor Burkhovetskiy, Boris Steinberg",
    venue: "13th Central & Eastern European Software Engineering Conference in Russia (CEE-SECR '17)",
    year: 2017,
    url: "https://doi.org/10.1016/j.procs.2017.11.165",
  },
  {
    title: "Combining parallelization with overlaps and optimization of cache memory usage",
    authors: "S.G. Ammaev, L.R. Gervich, B.Y. Steinberg",
    venue: "Parallel Computing Technologies (Springer)",
    year: 2017,
    url: "https://doi.org/10.1007/978-3-319-62932-2_24",
  },
  {
    title: "Automatic program parallelization with a block data distribution",
    authors: "L.R. Gervich, E.N. Kravchenko, B.Ya. Steinberg, M.V. Yurushkin",
    venue: "Numerical Analysis and Applications (Springer), vol. 8",
    year: 2015,
    url: "https://doi.org/10.1134/S1995423915010048",
  },
];
