package com.dairydash.data.db

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "farmers")
data class FarmerEntity(
    @PrimaryKey val farmerId: String,
    val name: String,
    val phone: String,
    val address: String,
    val cows: Int,
    val buffaloes: Int,
    val bankAccount: String,
    val center: String,
    val dailySupply: Double
)
