package co.edu.uptc.banco.cuenta;

import jakarta.persistence.LockModeType;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;

interface CuentaRepository extends JpaRepository<Cuenta, String> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select c from Cuenta c where c.telefono = ?1")
    Optional<Cuenta> bloquear(String telefono);
}

interface MovimientoRepository extends JpaRepository<Movimiento, Long> {
    List<Movimiento> findTop50ByTelefonoOrderByIdDesc(String telefono);
}
