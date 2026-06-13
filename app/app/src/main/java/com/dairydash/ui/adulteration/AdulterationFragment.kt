package com.dairydash.ui.adulteration

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.dairydash.R
import com.dairydash.databinding.FragmentAdulterationBinding
import com.dairydash.utils.SharedQualityData

class AdulterationFragment : Fragment() {

    private var _binding: FragmentAdulterationBinding? = null
    private val binding get() = _binding!!

    private val yesNoOptions = listOf("No", "Yes")

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentAdulterationBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupDropdowns()
        setupListeners()
    }

    private fun setupDropdowns() {
        val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, yesNoOptions)
        binding.spinnerUrea.setAdapter(adapter)
        binding.spinnerStarch.setAdapter(adapter)
        binding.spinnerDetergent.setAdapter(adapter)
        binding.spinnerSalt.setAdapter(adapter)

        binding.spinnerUrea.setText("No", false)
        binding.spinnerStarch.setText("No", false)
        binding.spinnerDetergent.setText("No", false)
        binding.spinnerSalt.setText("No", false)
    }

    private fun setupListeners() {
        binding.btnGenerateScore.setOnClickListener { analyzeAdulteration() }
        binding.btnProceedPayment.setOnClickListener {
            findNavController().navigate(R.id.paymentFragment)
        }
    }

    private fun analyzeAdulteration() {
        if (!SharedQualityData.hasQualityData()) {
            Toast.makeText(requireContext(), "Please complete Milk Quality Analysis first", Toast.LENGTH_SHORT).show()
            return
        }

        val water = binding.etWater.text?.toString()?.toFloatOrNull() ?: 0f
        val urea = binding.spinnerUrea.text?.toString() ?: "No"
        val starch = binding.spinnerStarch.text?.toString() ?: "No"
        val detergent = binding.spinnerDetergent.text?.toString() ?: "No"
        val salt = binding.spinnerSalt.text?.toString() ?: "No"

        var finalScore = SharedQualityData.baseScore.toDouble()
        val warnings = mutableListOf<String>()
        var isAdulterated = false

        if (water > 5) {
            finalScore -= (water - 5) * 2 // -2 points per % above 5%
            warnings.add("Water dilution detected: ${water}%")
        }
        if (starch == "Yes") { finalScore -= 20; warnings.add("Starch contamination detected (Score -20)"); isAdulterated = true }
        if (salt == "Yes") { finalScore -= 15; warnings.add("Salt contamination detected (Score -15)"); isAdulterated = true }
        if (urea == "Yes") { finalScore -= 50; warnings.add("CRITICAL: Urea detected (Score -50)"); isAdulterated = true }
        if (detergent == "Yes") { finalScore -= 60; warnings.add("CRITICAL: Detergent detected (Score -60)"); isAdulterated = true }

        val finalScoreInt = finalScore.coerceIn(0.0, 100.0).toInt()
        SharedQualityData.finalScore = finalScoreInt

        // Update UI
        binding.tvFinalScore.text = finalScoreInt.toString()

        // Build warning list dynamically
        binding.llWarnings.removeAllViews()
        warnings.forEach { warning ->
            val tv = TextView(requireContext()).apply {
                text = warning
                textSize = 13f
                setTextColor(ContextCompat.getColor(requireContext(), R.color.danger_dark))
                setPadding(24, 16, 24, 16)
                val lp = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                )
                lp.bottomMargin = 8
                layoutParams = lp
                setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.danger_light))
            }
            binding.llWarnings.addView(tv)
        }

        // Set status
        when {
            warnings.isEmpty() && water <= 5 -> {
                binding.tvAdulterationStatus.text = "Pure Milk"
                binding.tvAdulterationStatus.setBackgroundColor(
                    ContextCompat.getColor(requireContext(), R.color.success_light))
                binding.tvAdulterationStatus.setTextColor(
                    ContextCompat.getColor(requireContext(), R.color.success_dark))
            }
            isAdulterated || finalScoreInt < 50 -> {
                binding.tvAdulterationStatus.text = "Highly Adulterated"
                binding.tvAdulterationStatus.setBackgroundColor(
                    ContextCompat.getColor(requireContext(), R.color.danger_light))
                binding.tvAdulterationStatus.setTextColor(
                    ContextCompat.getColor(requireContext(), R.color.danger_dark))
            }
            else -> {
                binding.tvAdulterationStatus.text = "Moderately Adulterated"
                binding.tvAdulterationStatus.setBackgroundColor(
                    ContextCompat.getColor(requireContext(), R.color.warning_light))
                binding.tvAdulterationStatus.setTextColor(
                    ContextCompat.getColor(requireContext(), R.color.warning_dark))
            }
        }

        // Show result card with animation
        binding.cardResult.visibility = View.VISIBLE
        binding.cardResult.alpha = 0f
        binding.cardResult.animate().alpha(1f).setDuration(400).start()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
