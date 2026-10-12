/**
 * Types for the fixture contract handler (see contractHandler.mjs).
 *
 * The fixture payload is intentionally typed loosely: it is test/demo data, not
 * the API contract. Application code never imports this module.
 */
export declare const REVIEW_PREFIX: string
export declare function fixturePath(): string
export declare function loadFixture(): any
export declare function handleRequest(
  fixture: any,
  pathname: string,
  searchParams: URLSearchParams,
): { status: number; body: unknown }
