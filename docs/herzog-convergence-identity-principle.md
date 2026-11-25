# Herzog's Convergence–Identity Principle

**Research note — 2026-11-25**  
Ultimodel / BaguaCode / YanRiemann Requiem

> Convergence of representation need not imply convergence of identity.

## 1. The convergence theorem

For every fixed positive finite real number \(x\), define

$$U_n(x)=x^{1/n},\qquad n\in\mathbb N,\ n\ge1.$$

Since \(U_n(x)=\exp(\ln(x)/n)\), continuity of the exponential gives

$$\lim_{n\to\infty}U_n(x)=1.$$

Thus distinct inputs can share the same limiting representation. For example, 2 and 3 both converge to 1 under this operator. Equal limits do not imply equal inputs.

Reciprocal symmetry holds at every finite step:

$$U_n(x)U_n(1/x)=1.$$

## 2. The preservation theorem

Define the complementary coordinate

$$I_n(x)=n\ln U_n(x)=\ln x.$$

The pair

$$F_n(x)=(U_n(x),I_n(x))$$

therefore has the limit

$$F_\infty(x)=(1,\ln x).$$

The decoder \(D(1,z)=e^z\) satisfies \(D(F_\infty(x))=x\). In particular,

$$F_\infty(x)=F_\infty(y)\iff x=y.$$

The first coordinate becomes universal while the second preserves identity. Equivalently, the first-order deviation retains the same information:

$$\lim_{n\to\infty}n(U_n(x)-1)=\ln x.$$

This follows from \(\lim_{t\to0}(e^t-1)/t=1\), with \(x=1\) handled directly.

## 3. General theorem: the boundary of recoverability

Let \(R:X\to Y\) be a representation and \(I:X\to Z\) a complementary coordinate. Define \(F(x)=(R(x),I(x))\).

**Theorem.** The following are equivalent:

1. \(F\) is injective.
2. There exists a decoder \(D:F(X)\to X\) with \(D\circ F=\operatorname{id}_X\).
3. For every \(y\in R(X)\), the restriction of \(I\) to the fiber \(R^{-1}(\{y\})\) is injective.

**Proof.** (1) implies (2) because the inverse of an injective map is well-defined on its image. (2) implies (1) by applying the decoder to equal representations. For (1) implies (3), two points in the same fiber with equal complementary coordinates have equal pairs and hence are identical. Conversely, if two pairs are equal, their inputs lie in the same fiber and share a complementary coordinate, so (3) implies they are identical. QED.

**Anti-inference corollary.** If \(R\) is not injective, there exist distinct \(a,b\) with \(R(a)=R(b)\). Consequently the equality of their representations alone cannot establish equality of their identities in general. This is a limitation on an inference, not a refutation of mathematical proof.

Distinct representations under the same deterministic map do imply distinct inputs, but do not establish statistical or logical independence.

## 4. Discrete analogue: HEX 6+2

For an integer byte \(0\le b\le255\), define

$$L=b\bmod64,\qquad H=\lfloor b/64\rfloor.$$

Euclidean division gives \(b=64H+L\), with \(0\le L\le63\) and \(0\le H\le3\). The combined encoding is bijective onto the product of those ranges. Each coordinate alone is non-injective.

For example, 1 and 65 share low coordinate 1; the high coordinate distinguishes them.

The shared principle is exact recoverability through complementary information, not that the byte decomposition itself is an asymptotic convergence operation. The split preserves eight bits of capacity in total; it does not guarantee compression.

## 5. Consequences and limitations

- Universal convergence of one coordinate is compatible with distinct recoverable identities.
- The complement need only distinguish points within each representation fiber.
- Agreement between numerical engines on selected outputs is not sufficient evidence that their underlying models are identical.
- The result concerns fixed positive finite real inputs, not zero, negative inputs, or arbitrary sequences growing with n. For example, \((n!)^{1/n}\sim n/e\), not 1.
- Exact real arithmetic is assumed. In floating point, \(U_n(x)\) can round to 1; computing the complement from that rounded value may lose information. Retain \(\ln x\) directly when needed.
- No solution of the three-body problem or Riemann hypothesis follows from this theorem alone. Neither unlimited lossless compression nor the impossibility of mathematical proof is established.
- The mathematical ingredients (injectivity, inverse maps on images, fibers, exponential limits, Euclidean division) are standard. The proposed name and project-specific synthesis are not a claim of verified mathematical novelty.

## 6. Project interpretation

> Every description is a model, not the thing itself.

A representation can establish identity within a specified domain to the extent that it preserves distinctions between possible identities.

Convergence without distinguishing information cannot generally establish identity. Convergence with sufficient distinguishing information permits exact reconstruction.

**Unity can be universal without individuality being destroyed.**
