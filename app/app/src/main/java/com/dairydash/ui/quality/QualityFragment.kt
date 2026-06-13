package com.dairydash.ui.quality

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.dairydash.R
import com.dairydash.data.db.AppDatabase
import com.dairydash.databinding.FragmentQualityBinding
import com.dairydash.utils.SharedQualityData
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class QualityFragment : Fragment() {

    private var _binding: FragmentQualityBinding? = null
    private val binding get() = _binding!!

    private val milkTypes = listOf("Cow", "Buffalo", "Mixed")
    private val farmerNames = mutableListOf<String>()
    private val farmerIds = mutableListOf<String>()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentQualityBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupDropdowns()
        loadFarmers()
        setupListeners()
    }

    private fun setupDropdowns() {
        // Milk type dropdown
        val milkAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, milkTypes)
        binding.spinnerMilkType.setAdapter(milkAdapter)
        binding.spinnerMilkType.setText("Cow", false)
    }

    private fun loadFarmers() {
        val db = AppDatabase.getInstance(requireContext())
        CoroutineScope(Dispatchers.IO).launch {
            val farmers = db.farmerDao().getAllFarmersList()
            withContext(Dispatchers.Main) {
                farmerIds.clear()
                farmerNames.clear()
                farmers.forEach { f ->
                    farmerIds.add(f.farmerId)
                    farmerNames.add("${f.farmerId} - ${f.name}")
                }
                val farmerAdapter = ArrayAdapter(
                    requireContext(),
                    android.R.layout.simple_dropdown_item_1line,
                    farmerNames
                )
                binding.spinnerFarmer.setAdapter(farmerAdapter)
            }
        }
    }

    private fun setupListeners() {
        binding.btnAnalyze.setOnClickListener { calculateBaseQuality() }
        binding.btnNext.setOnClickListener {
            findNavController().navigate(R.id.adulterationFragment)
        }
    }

    private fun calculateBaseQuality() {
        val farmerText = binding.spinnerFarmer.text.toString()
        val qty = binding.etQuantity.text?.toString()?.toDoubleOrNull()
        val fat = binding.etFat.text?.toString()?.toDoubleOrNull()
        val snf = binding.etSnf.text?.toString()?.toDoubleOrNull()

        if (farmerText.isBlank() || farmerText == getString(R.string.select_farmer_hint) ||
            qty == null || fat == null || snf == null) {
            Toast.makeText(requireContext(), "Please fill all required fields correctly", Toast.LENGTH_SHORT).show()
            return
        }

        // Determine farmer ID from selection
        val selectedIdx = farmerNames.indexOf(farmerText)
        val farmerId = if (selectedIdx >= 0) farmerIds[selectedIdx] else farmerText

        // Save state
        SharedQualityData.farmerId = farmerId
        SharedQualityData.qty = qty
        SharedQualityData.fat = fat
        SharedQualityData.snf = snf

        // Calculate score: Ideal cow: Fat>=3.5, SNF>=8.5
        var score = 100
        if (fat < 3.5) score -= ((3.5 - fat) * 10).toInt()
        if (snf < 8.5) score -= ((8.5 - snf) * 10).toInt()
        score = score.coerceIn(0, 100)
        SharedQualityData.baseScore = score

        // Update UI
        binding.progressScore.progress = score
        binding.tvScore.text = score.toString()

        val (statusText, bgColor, textColor) = when {
            score >= 90 -> Triple("Excellent", R.color.success_light, R.color.success_dark)
            score >= 75 -> Triple("Good", R.color.primary_container, R.color.primary_dark)
            else        -> Triple("Average / Poor", R.color.danger_light, R.color.danger_dark)
        }

        binding.tvStatus.text = statusText
        binding.tvStatus.setBackgroundColor(requireContext().getColor(bgColor))
        binding.tvStatus.setTextColor(requireContext().getColor(textColor))

        // Show result card with animation
        binding.cardResult.visibility = View.VISIBLE
        binding.cardResult.alpha = 0f
        binding.cardResult.animate().alpha(1f).setDuration(400).start()
    }

    override fun onResume() {
        super.onResume()
        // Reload farmers in case new ones were added
        loadFarmers()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
