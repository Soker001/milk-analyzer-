package com.dairydash.ui.farmers

import android.app.Application
import androidx.lifecycle.*
import com.dairydash.data.db.AppDatabase
import com.dairydash.data.db.FarmerEntity
import com.dairydash.data.repository.FarmerRepository
import kotlinx.coroutines.launch

class FarmerViewModel(application: Application) : AndroidViewModel(application) {

    private val repository: FarmerRepository
    val allFarmers: LiveData<List<FarmerEntity>>

    private val _uiEvent = MutableLiveData<String>()
    val uiEvent: LiveData<String> = _uiEvent

    init {
        val db = AppDatabase.getInstance(application)
        repository = FarmerRepository(db.farmerDao())
        allFarmers = repository.allFarmers
    }

    fun addFarmer(
        farmerId: String, name: String, phone: String, address: String,
        cows: Int, buffaloes: Int, bankAccount: String, center: String,
        dailySupply: Double
    ) {
        if (farmerId.isBlank() || name.isBlank() || phone.isBlank() ||
            address.isBlank() || bankAccount.isBlank() || center.isBlank()) {
            _uiEvent.value = "ERROR:Please fill all required fields"
            return
        }
        viewModelScope.launch {
            val farmer = FarmerEntity(
                farmerId = farmerId.trim(),
                name = name.trim(),
                phone = phone.trim(),
                address = address.trim(),
                cows = cows,
                buffaloes = buffaloes,
                bankAccount = bankAccount.trim(),
                center = center.trim(),
                dailySupply = dailySupply
            )
            repository.insertFarmer(farmer)
            _uiEvent.value = "SUCCESS:Farmer added successfully!"
        }
    }

    fun deleteFarmer(farmer: FarmerEntity) {
        viewModelScope.launch {
            repository.deleteFarmer(farmer)
            _uiEvent.value = "SUCCESS:Farmer deleted"
        }
    }
}
