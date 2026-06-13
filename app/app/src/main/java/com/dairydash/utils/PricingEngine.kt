package com.dairydash.utils

/**
 * Kotlin port of pricing_engine.py
 * Calculates milk price per litre based on state, fat%, SNF%, quantity, and quality score.
 */
object PricingEngine {

    data class PricingResult(
        val success: Boolean,
        val state: String = "",
        val basePricePerLitre: Double = 0.0,
        val finalPricePerLitre: Double = 0.0,
        val qualityScore: Double = 0.0,
        val quantity: Double = 0.0,
        val totalPayment: Double = 0.0,
        val error: String = ""
    )

    fun calculatePrice(
        state: String,
        fat: Double,
        snf: Double,
        quantity: Double,
        qualityScore: Double
    ): PricingResult {
        return try {
            val basePricePerLitre = when (state) {
                "Tamil Nadu"  -> (fat * 7.0) + (snf * 3.0)
                "Kerala"      -> (fat * 6.8) + (snf * 3.2)
                "Karnataka"   -> {
                    val basePrice = 30.0
                    val fatIncentive = if (fat > 3.5) (fat - 3.5) * 2.0 else 0.0
                    val subsidy = 5.0
                    basePrice + fatIncentive + subsidy
                }
                "Gujarat"     -> (fat * 6.5) + (snf * 4.0)
                "Maharashtra" -> fat * 8.0
                "Punjab"      -> (fat * 7.5) + (snf * 2.5)
                "Haryana"     -> (fat * 7.2) + (snf * 2.8)
                else          -> (fat * 6.5) + (snf * 3.0) // Default fallback
            }

            // Apply quality score impact: score 100 → full price; score 50 → 50% of price
            val finalPricePerLitre = basePricePerLitre * (qualityScore / 100.0)
            val totalPayment = finalPricePerLitre * quantity

            PricingResult(
                success = true,
                state = state,
                basePricePerLitre = round2(basePricePerLitre),
                finalPricePerLitre = round2(finalPricePerLitre),
                qualityScore = qualityScore,
                quantity = quantity,
                totalPayment = round2(totalPayment)
            )
        } catch (e: Exception) {
            PricingResult(success = false, error = e.message ?: "Unknown error")
        }
    }

    fun getFormulaText(state: String): String = when (state) {
        "Tamil Nadu"  -> "Price = (Fat × 7) + (SNF × 3)"
        "Kerala"      -> "Price = (Fat × 6.8) + (SNF × 3.2)"
        "Gujarat"     -> "Price = (Fat × 6.5) + (SNF × 4)"
        "Maharashtra" -> "Price = Fat × 8"
        "Karnataka"   -> "Price = Base(30) + Fat Incentive(>3.5) + Subsidy(5)"
        "Punjab"      -> "Price = (Fat × 7.5) + (SNF × 2.5)"
        "Haryana"     -> "Price = (Fat × 7.2) + (SNF × 2.8)"
        else          -> "Standard Formula"
    }

    private fun round2(value: Double): Double =
        Math.round(value * 100.0) / 100.0
}
