-- Delta_680 and the end of its descent, checked with the Polyhedra package.
needsPackage "Polyhedra"
passes = 0; fails = 0;
verify = (ok, what) -> (
    if ok then (passes = passes + 1; print("PASS " | what))
    else (fails = fails + 1; print("FAIL " | what)));

D = convexHull transpose matrix {{-1,-1,-1,-1},{83,-1,-1,-1},{-1,6,-1,-1},{-1,-1,2,-1},{-1,-1,-1,1}};
verify(isReflexive D, "Delta_680 is reflexive");
verify(#(latticePoints D) == 680, "Delta_680 has 680 lattice points");
Ds = polar D;
verify(#(latticePoints Ds) == 26, "its dual has 26 lattice points");
verify(24 * volume D == 3528, "normalised volume of Delta_680 is 3528");
verify(24 * volume Ds == 84, "normalised volume of the dual is 84");
verify(numColumns vertices Ds == 5 and isSimplicial Ds, "the dual is a simplex");
W = set apply(numColumns vertices Ds, i -> apply(flatten entries (vertices Ds)_{i}, x -> lift(x, ZZ)));
verify(W === set {{1,0,0,0},{0,1,0,0},{0,0,1,0},{0,0,0,1},{-1,-12,-28,-42}},
      "the dual has vertices e1, e2, e3, e4 and (-1,-12,-28,-42)");

E = convexHull transpose matrix {{-1,-1,-1,1},{-1,-1,2,-1},{-1,0,1,-1},{-1,6,-1,-1},{1,0,0,0}};
verify(isReflexive E, "the end simplex Gamma_38 is reflexive");
verify(#(latticePoints E) == 9, "Gamma_38 has 9 lattice points");
verify(#(latticePoints polar E) == 201, "its dual has 201 lattice points");
verify(contains(D, E), "Gamma_38 lies in Delta_680");

print("delta680.m2: " | toString passes | " passed, " | toString fails | " failed");
if fails > 0 then exit 1 else exit 0;
