// Thin client for the backend's self-serve billing routes
// (backend/app/routers/billing.py). Kept dependency-light (axios, already
// a project dependency) so it's easy to read alongside the routes it calls.
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";

/**
 * Start a Stripe Checkout flow for a self-serve plan ("pro" | "team").
 * Returns { checkoutUrl } on success. Throws an Error with a `.code` of
 * "billing_not_configured" when Stripe hasn't been set up yet in the
 * deploy environment (a real, expected pre-launch state — not a bug) so
 * callers can show a friendly message instead of a raw failure.
 */
export async function startCheckout(planKey, customerEmail) {
  try {
    const res = await axios.post(`${BACKEND_URL}/api/billing/checkout`, {
      plan: planKey,
      ...(customerEmail ? { customer_email: customerEmail } : {}),
    });
    return { checkoutUrl: res.data.checkout_url, sessionId: res.data.session_id };
  } catch (err) {
    const data = err?.response?.data;
    const message =
      data?.message ||
      (err?.response?.status === 503
        ? "Checkout isn't turned on yet — reach out and we'll set you up by hand."
        : "Something went wrong starting checkout. Please try again or email us.");
    const wrapped = new Error(message);
    wrapped.code = data?.error || "checkout_failed";
    wrapped.status = err?.response?.status;
    throw wrapped;
  }
}
