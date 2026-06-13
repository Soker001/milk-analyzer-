package com.dairydash.utils

/**
 * Shared in-memory state passed between Quality → Adulteration → Payment screens.
 * This mirrors the web app's currentQualityData global variable.
 */
object SharedQualityData {
    var farmerId: String = ""
    var qty: Double = 0.0
    var fat: Double = 0.0
    var snf: Double = 0.0
    var baseScore: Int = 0
    var finalScore: Int = 0

    fun reset() {
        farmerId = ""
        qty = 0.0
        fat = 0.0
        snf = 0.0
        baseScore = 0
        finalScore = 0
    }

    fun hasQualityData(): Boolean = baseScore > 0 || (qty > 0 && fat > 0 && snf > 0)
    fun hasFinalScore(): Boolean = finalScore >= 0 && hasQualityData()
}
