package com.dairydash.ui.payment

import android.animation.ValueAnimator
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.dairydash.R
import com.dairydash.databinding.FragmentPaymentBinding
import com.dairydash.utils.PricingEngine
import com.dairydash.utils.SharedQualityData

class PaymentFragment : Fragment() {

    private var _binding: FragmentPaymentBinding? = null
    private val binding get() = _binding!!

    private val states = listOf(
        "Tamil Nadu", "Kerala", "Karnataka",
        "Gujarat", "Maharashtra", "Punjab", "Haryana"
    )

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentPaymentBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupDropdown()
        populateSummary()
        setupListeners()
    }

    private fun setupDropdown() {
        val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, states)
        binding.spinnerState.setAdapter(adapter)
    }

    private fun populateSummary() {
        binding.tvSummaryQty.text = "${SharedQualityData.qty} L"
        binding.tvSummaryFat.text = "${SharedQualityData.fat} %"
        binding.tvSummarySnf.text = "${SharedQualityData.snf} %"
        binding.tvSummaryScore.text = "${SharedQualityData.finalScore} / 100"
    }

    private fun setupListeners() {
        binding.btnCalculate.setOnClickListener { calculateFinalPrice() }
        binding.btnProcessPayment.setOnClickListener { processPayment() }
    }

    private fun calculateFinalPrice() {
        if (!SharedQualityData.hasFinalScore()) {
            Toast.makeText(requireContext(), "Please complete Quality & Adulteration analysis", Toast.LENGTH_SHORT).show()
            return
        }

        val state = binding.spinnerState.text?.toString() ?: ""
        if (state.isBlank() || state == getString(R.string.select_state_hint) || !states.contains(state)) {
            Toast.makeText(requireContext(), "Please select a state", Toast.LENGTH_SHORT).show()
            return
        }

        // Show payment result card
        binding.cardPaymentResult.visibility = View.VISIBLE
        binding.llLoading.visibility = View.VISIBLE
        binding.llPaymentDetails.visibility = View.GONE

        // Calculate using PricingEngine
        val result = PricingEngine.calculatePrice(
            state = state,
            fat = SharedQualityData.fat,
            snf = SharedQualityData.snf,
            quantity = SharedQualityData.qty,
            qualityScore = SharedQualityData.finalScore.toDouble()
        )

        if (!result.success) {
            binding.llLoading.visibility = View.GONE
            Toast.makeText(requireContext(), "Error: ${result.error}", Toast.LENGTH_SHORT).show()
            return
        }

        // Simulate loading delay (matches web app animation feel)
        binding.root.postDelayed({
            binding.llLoading.visibility = View.GONE
            binding.llPaymentDetails.visibility = View.VISIBLE

            binding.tvFormula.text = PricingEngine.getFormulaText(state)
            binding.tvBasePrice.text = "₹${"%.2f".format(result.basePricePerLitre)}"
            binding.tvFinalPrice.text = "₹${"%.2f".format(result.finalPricePerLitre)}"

            // Animated counter for total payment
            animateCounter(result.totalPayment)
        }, 600)
    }

    private fun animateCounter(finalValue: Double) {
        val animator = ValueAnimator.ofFloat(0f, finalValue.toFloat())
        animator.duration = 800
        animator.addUpdateListener { anim ->
            val value = anim.animatedValue as Float
            binding.tvTotal.text = "₹${"%.2f".format(value)}"
        }
        animator.start()
    }

    private fun processPayment() {
        Toast.makeText(
            requireContext(),
            "Payment processed successfully and saved!",
            Toast.LENGTH_LONG
        ).show()

        // Reset shared state and navigate back to farmers
        binding.root.postDelayed({
            SharedQualityData.reset()
            findNavController().navigate(R.id.farmerFragment)
        }, 1500)
    }

    override fun onResume() {
        super.onResume()
        populateSummary()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
